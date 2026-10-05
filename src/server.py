import os
import json
import logging
from flask import Flask, request, send_file, abort, jsonify, redirect, make_response, render_template, Response
import tempfile
import zipfile
from .evidence import ensure_thumbnail
import time
from collections import defaultdict, deque
from datetime import datetime
from .stream_manager import get_stream_manager
from .activity_tracker import get_activity_tracker
import psutil
import cv2
import secrets
import hmac
from flask_wtf.csrf import CSRFProtect, generate_csrf
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize logger
logger = logging.getLogger(__name__)

# Check if database mode is enabled
USE_DATABASE = os.getenv('USE_DATABASE', 'false').lower() == 'true'

if USE_DATABASE:
    from .database import (
        init_database, get_all_evidence, get_evidence_by_id,
        update_evidence_resolution, get_evidence_stats, count_evidence,
        generate_pairing_code, verify_pairing_code, register_device,
        get_all_devices, get_device_by_id, get_device_by_token,
        update_device_last_seen, revoke_device, log_device_activity,
        get_device_stats, cleanup_expired_pairing_codes
    )
    logger.info("Server running in DATABASE mode")
    # Initialize database on startup
    init_database()
else:
    logger.info("Server running in JSON mode")

EVIDENCE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'evidence')

# Basic token-based roles: ADMIN_TOKEN, SECURITY_TOKEN, VIEWER_TOKEN
ADMIN_TOKEN = os.getenv('ADMIN_TOKEN', '')
SECURITY_TOKEN = os.getenv('SECURITY_TOKEN', '')
VIEWER_TOKEN = os.getenv('VIEWER_TOKEN', '')

ROLE_MAP = {
    ADMIN_TOKEN: 'admin',
    SECURITY_TOKEN: 'security',
    VIEWER_TOKEN: 'viewer',
}

# Configure Flask to use templates directory
template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Configure Flask secret key for CSRF protection
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(32))
app.config['WTF_CSRF_TIME_LIMIT'] = None  # No expiration for CSRF tokens
app.config['WTF_CSRF_SSL_STRICT'] = False  # Allow development without HTTPS
app.config['WTF_CSRF_HEADERS'] = ['X-CSRFToken', 'X-CSRF-Token']  # Accept CSRF from headers

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Add security headers
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    # Allow Bootstrap CDN for CSS, JS, and fonts
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; img-src 'self' data:; font-src 'self' https://cdn.jsdelivr.net"
    return response


def safe_token_compare(token: str, expected: str) -> bool:
    """Constant-time token comparison to prevent timing attacks"""
    if not token or not expected:
        return False
    return hmac.compare_digest(token, expected)

def require_role(allowed_roles):
    def wrapper(fn):
        def inner(*args, **kwargs):
            # Accept token via header or cookie only (NOT query params for security)
            token = (
                request.headers.get('X-Auth-Token')
                or request.cookies.get('auth_token')
                or ''
            )
            # Use constant-time comparison
            role = None
            for expected_token, token_role in ROLE_MAP.items():
                if expected_token and safe_token_compare(token, expected_token):
                    role = token_role
                    break
            
            if role in allowed_roles:
                return fn(*args, **kwargs)
            return abort(403)
        inner.__name__ = fn.__name__
        return inner
    return wrapper

_rate_buckets = defaultdict(lambda: deque(maxlen=200))

def rate_limit(max_per_minute: int = 60):
    window = 60.0
    def decorator(fn):
        def inner(*args, **kwargs):
            ip = request.remote_addr or 'unknown'
            key = (ip, request.path)
            now = time.time()
            q = _rate_buckets[key]
            # purge old
            while q and now - q[0] > window:
                q.popleft()
            if len(q) >= max_per_minute:
                return abort(429)
            q.append(now)
            return fn(*args, **kwargs)
        inner.__name__ = fn.__name__
        return inner
    return decorator

def get_token() -> str:
    return (
        request.headers.get('X-Auth-Token')
        or request.cookies.get('auth_token')
        or ''
    )

def get_role_from_token(token: str):
    """Get role using constant-time comparison"""
    if not token:
        return None
    for expected_token, role in ROLE_MAP.items():
        if expected_token and safe_token_compare(token, expected_token):
            return role
    return None

@app.get('/')
def index():
    # Redirect to dashboard if authenticated, otherwise show login
    token = get_token()
    if token and get_role_from_token(token):
        return redirect('/dashboard')
    return redirect('/login')

@app.get('/login')
def login_get():
    # If already authenticated, redirect to dashboard
    token = get_token()
    if token and get_role_from_token(token):
        return redirect('/dashboard')
    return render_template('login.html')

@app.post('/login')
def login_post():
    token = request.form.get('token', '')
    if not token:
        return render_template('login.html', error='Token is required'), 400
    
    # Validate token against known roles
    role = get_role_from_token(token)
    if not role:
        return render_template('login.html', error='Invalid access token'), 403
    
    resp = make_response(redirect('/dashboard'))
    # Secure cookie with HTTPOnly, Secure (for HTTPS), and SameSite protection
    resp.set_cookie('auth_token', token, httponly=True, secure=True, samesite='Strict', max_age=43200)  # 12 hours
    return resp

@app.post('/logout')
def logout():
    resp = make_response(redirect('/'))
    resp.delete_cookie('auth_token')
    return resp

def get_evidence_list(date_range='all', rule_type='all', camera_filter='all', limit=1000, offset=0):
    """Get evidence list from database or JSON files"""
    if USE_DATABASE:
        return get_all_evidence(
            date_range=date_range,
            rule_type=rule_type,
            camera_filter=camera_filter,
            limit=limit,
            offset=offset
        )
    else:
        # Legacy JSON mode
        items = []
        for fname in os.listdir(EVIDENCE_DIR):
            if fname.endswith('.json'):
                with open(os.path.join(EVIDENCE_DIR, fname), 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                items.append(meta)
        return items


@app.get('/evidence')
@require_role(['admin', 'security', 'viewer'])
@rate_limit(120)
def list_evidence():
    items = get_evidence_list()
    return jsonify(items)

@app.get('/evidence/image')
@require_role(['admin', 'security'])
@rate_limit(120)
def get_image():
    # Only accept filename-based access (not arbitrary paths) for security
    name = request.args.get('name')
    if not name:
        return abort(404)
    
    # Validate filename - only allow safe characters
    if not name or '..' in name or '/' in name or '\\' in name:
        return abort(403)
    
    evidence_root = os.path.realpath(EVIDENCE_DIR)
    path = os.path.join(EVIDENCE_DIR, name)
    
    # Normalize and enforce evidence directory containment
    real_path = os.path.realpath(path)
    if not real_path.startswith(evidence_root):
        return abort(403)
    if not os.path.exists(real_path):
        return abort(404)
    try:
        return send_file(real_path)
    except Exception:
        return abort(500)

@app.get('/evidence/export')
@require_role(['admin', 'security'])
@rate_limit(30)
def export_zip():
    tmp_fd, tmp_path = tempfile.mkstemp(suffix='.zip')
    os.close(tmp_fd)
    with zipfile.ZipFile(tmp_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for fname in os.listdir(EVIDENCE_DIR):
            if fname.endswith('.jpg') or fname.endswith('.json'):
                zf.write(os.path.join(EVIDENCE_DIR, fname), arcname=fname)
    return send_file(tmp_path, as_attachment=True, download_name='autoguard_evidence.zip')

@app.get('/dashboard')
@require_role(['admin', 'security', 'viewer'])
@rate_limit(60)
def dashboard():
    token = get_token()
    role = get_role_from_token(token) or 'anonymous'
    
    # Get filter parameters
    date_range = request.args.get('date_range', 'all')
    rule_type = request.args.get('rule_type', 'all')
    camera_filter = request.args.get('camera', 'all')
    page = int(request.args.get('page', 1))
    per_page = 12
    
    if USE_DATABASE:
        # Database mode - use database queries
        # Get statistics
        stats = get_evidence_stats()
        total_incidents = stats['total_incidents']
        high_priority = stats['high_priority']
        theft_alerts = stats['theft_alerts']
        resolved = stats['resolved']
        
        # Count filtered results
        total_filtered = count_evidence(date_range, rule_type, camera_filter)
        
        # Calculate pagination
        total_pages = max(1, (total_filtered + per_page - 1) // per_page)
        page = max(1, min(page, total_pages))
        offset = (page - 1) * per_page
        
        # Get paginated evidence from database
        evidence_data = get_all_evidence(
            date_range=date_range,
            rule_type=rule_type,
            camera_filter=camera_filter,
            limit=per_page,
            offset=offset
        )
        
        # Format evidence for template
        paginated_evidence = []
        for item in evidence_data:
            img_path = item.get('image_path', '')
            image_name = os.path.basename(img_path) if img_path else ''
            timestamp = item.get('timestamp', '')
            timestamp_short = timestamp.split(' ')[1] if ' ' in timestamp else timestamp
            
            paginated_evidence.append({
                'id': item.get('id', ''),
                'image_name': image_name,
                'rule': item.get('rule', ''),
                'timestamp': timestamp,
                'timestamp_short': timestamp_short,
                'person_id': item.get('person_id', 0),
                'camera_id': item.get('camera_id', 'CAM01'),
                'priority': item.get('priority', 'standard'),
                'description': item.get('description', ''),
                'resolved': bool(item.get('resolved', False))
            })
    else:
        # Legacy JSON mode
        evidence_list = []
        for fname in os.listdir(EVIDENCE_DIR):
            if fname.endswith('.json'):
                with open(os.path.join(EVIDENCE_DIR, fname), 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                
                img_path = meta.get('image_path', '')
                image_name = os.path.basename(img_path) if img_path else ''
                rule = meta.get('rule', '')
                timestamp = meta.get('timestamp', '')
                person_id = meta.get('person_id', 0)
                
                # Determine priority
                priority = meta.get('priority', 'standard')
                if not priority:
                    priority = 'high' if any(x in rule.lower() for x in ['aggressive', 'violence', 'threat', 'weapon', 'freeze']) else 'standard'
                
                timestamp_short = timestamp.split(' ')[1] if ' ' in timestamp else timestamp
                description = meta.get('description', '')
                resolved_status = meta.get('resolved', False)
                
                evidence_list.append({
                    'id': fname.replace('.json', ''),
                    'image_name': image_name,
                    'rule': rule,
                    'timestamp': timestamp,
                    'timestamp_short': timestamp_short,
                    'person_id': person_id,
                    'camera_id': meta.get('camera_id', 'CAM01'),
                    'priority': priority,
                    'description': description,
                    'resolved': resolved_status
                })
        
        # Sort by timestamp (newest first)
        evidence_list.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Apply filters
        filtered_evidence = evidence_list.copy()
        
        # Date range filter
        if date_range != 'all':
            from datetime import datetime, timedelta
            now = datetime.now()
            
            if date_range == 'today':
                cutoff = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif date_range == 'week':
                cutoff = now - timedelta(days=7)
            elif date_range == 'month':
                cutoff = now - timedelta(days=30)
            else:
                cutoff = None
            
            if cutoff:
                filtered_evidence = [
                    e for e in filtered_evidence
                    if datetime.strptime(e['timestamp'], '%Y-%m-%d %H:%M:%S') >= cutoff
                ]
        
        # Rule type filter
        if rule_type != 'all':
            rule_map = {
                'loitering': 'Loitering',
                'exit_checkout': 'Exit Without Checkout',
                'shelf_exit': 'Shelf',
                'violence': 'violence'
            }
            search_term = rule_map.get(rule_type, rule_type)
            filtered_evidence = [e for e in filtered_evidence if search_term.lower() in e['rule'].lower()]
        
        # Camera filter
        if camera_filter != 'all':
            filtered_evidence = [e for e in filtered_evidence if e['camera_id'] == camera_filter]
        
        # Calculate statistics
        total_incidents = len(evidence_list)
        high_priority = sum(1 for e in evidence_list if e['priority'] == 'high')
        theft_alerts = sum(1 for e in evidence_list if e['priority'] == 'standard')
        resolved = sum(1 for e in evidence_list if e.get('resolved', False))
        
        # Pagination
        total_filtered = len(filtered_evidence)
        total_pages = max(1, (total_filtered + per_page - 1) // per_page)
        page = max(1, min(page, total_pages))
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_evidence = filtered_evidence[start_idx:end_idx]
    
    return render_template('dashboard.html',
                         role=role,
                         token=token,
                         evidence=paginated_evidence,
                         total_incidents=total_incidents,
                         high_priority=high_priority,
                         theft_alerts=theft_alerts,
                         resolved=resolved,
                         current_page=page,
                         total_pages=total_pages,
                         date_range=date_range,
                         rule_type=rule_type,
                         camera_filter=camera_filter,
                         request=request)

@app.get('/evidence/thumb')
@require_role(['admin', 'security', 'viewer'])
@rate_limit(240)
def thumb():
    name = request.args.get('name')
    if not name:
        return abort(404)
    
    img_path = os.path.join(EVIDENCE_DIR, name)
    if not os.path.exists(img_path):
        return abort(404)
    
    thumb_dir = os.path.join(EVIDENCE_DIR, 'thumbnails')
    
    try:
        tpath = ensure_thumbnail(img_path, thumb_dir)
        
        # If thumbnail generation failed or doesn't exist, serve original
        if not os.path.exists(tpath):
            return send_file(img_path)
        
        return send_file(tpath)
    except Exception as e:
        # Fallback to original image if thumbnail fails
        try:
            return send_file(img_path)
        except Exception:
            return abort(500)

@app.get('/live')
@require_role(['admin', 'security', 'viewer'])
def live_feed():
    token = get_token()
    role = get_role_from_token(token) or 'anonymous'
    return render_template('live.html', role=role, token=token, request=request)

@app.get('/video_feed')
@require_role(['admin', 'security', 'viewer'])
def video_feed():
    """Video streaming endpoint"""
    def generate():
        stream_mgr = get_stream_manager()
        stream_mgr.add_client()
        try:
            while True:
                frame_bytes = stream_mgr.get_jpeg_frame()
                if frame_bytes:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                time.sleep(0.033)  # ~30 FPS
        finally:
            stream_mgr.remove_client()
    
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.get('/stream_stats')
@require_role(['admin', 'security', 'viewer'])
def stream_stats():
    """Get streaming statistics"""
    stream_mgr = get_stream_manager()
    return jsonify(stream_mgr.get_stats())

@app.get('/live_activity')
@require_role(['admin', 'security', 'viewer'])
def live_activity():
    """Get live activity statistics"""
    activity_tracker = get_activity_tracker()
    activity = activity_tracker.get_activity()
    detections = activity_tracker.get_recent_detections()
    
    # Get system performance metrics
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        memory_gb = memory.used / (1024**3)
        memory_percent = memory.percent
    except Exception:
        cpu_percent = 0
        memory_gb = 0
        memory_percent = 0
    
    return jsonify({
        'activity': activity,
        'recent_detections': detections,
        'system': {
            'cpu_percent': cpu_percent,
            'memory_gb': round(memory_gb, 1),
            'memory_percent': memory_percent
        }
    })

@app.get('/snapshot')
@require_role(['admin', 'security', 'viewer'])
def snapshot():
    """Capture a snapshot from the live feed"""
    stream_mgr = get_stream_manager()
    frame = stream_mgr.get_frame()
    
    if frame is None:
        return abort(404)
    
    # Generate filename with timestamp
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"snapshot_CAM01_{timestamp}.jpg"
    
    # Encode as JPEG
    ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
    if not ret:
        return abort(500)
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
    temp_file.write(buffer.tobytes())
    temp_file.close()
    
    return send_file(temp_file.name, as_attachment=True, download_name=filename)

@app.get('/test-pairing')
def test_pairing():
    """Test page for device pairing"""
    return render_template('test_pairing.html')

@app.get('/devices')
@require_role(['admin'])
def devices():
    token = get_token()
    role = get_role_from_token(token) or 'anonymous'
    
    # Get device data if database mode is enabled
    devices_list = []
    stats = {'total': 0, 'active': 0, 'idle': 0}
    
    if USE_DATABASE:
        devices_list = get_all_devices()
        stats = get_device_stats()
        
        # Add time ago helper for each device
        from datetime import datetime, timezone
        now = datetime.now()
        
        for device in devices_list:
            if device.get('last_seen'):
                try:
                    last_seen = datetime.strptime(device['last_seen'], "%Y-%m-%d %H:%M:%S")
                    delta = now - last_seen
                    
                    if delta.seconds < 300:  # Less than 5 minutes
                        device['time_ago'] = f"{delta.seconds // 60} minutes ago"
                        device['status'] = 'active'
                        device['status_color'] = 'success'
                    elif delta.seconds < 3600:  # Less than 1 hour
                        device['time_ago'] = f"{delta.seconds // 60} minutes ago"
                        device['status'] = 'idle'
                        device['status_color'] = 'warning'
                    elif delta.days == 0:
                        device['time_ago'] = f"{delta.seconds // 3600} hours ago"
                        device['status'] = 'idle'
                        device['status_color'] = 'warning'
                    else:
                        device['time_ago'] = f"{delta.days} days ago"
                        device['status'] = 'inactive'
                        device['status_color'] = 'secondary'
                except:
                    device['time_ago'] = 'Unknown'
                    device['status'] = 'unknown'
                    device['status_color'] = 'secondary'
            else:
                device['time_ago'] = 'Never'
                device['status'] = 'inactive'
                device['status_color'] = 'secondary'
    
    return render_template('devices.html', 
                         role=role, 
                         token=token, 
                         request=request,
                         devices=devices_list,
                         stats=stats)

@app.get('/incidents')
@require_role(['admin', 'security', 'viewer'])
def incidents():
    # Redirect to dashboard for now (same view)
    return redirect('/dashboard')

@app.get('/config')
@require_role(['admin'])
def config():
    # Placeholder for configuration UI
    return "<h2>Configuration UI - Coming Soon</h2><p><a href='/dashboard'>Back to Dashboard</a></p>"

@app.get('/whoami')
def whoami():
    token = get_token()
    role = get_role_from_token(token) or 'anonymous'
    return {'role': role}

@app.post('/evidence/<evidence_id>/resolve')
@require_role(['admin', 'security'])
def resolve_evidence(evidence_id):
    """Mark an incident as resolved"""
    try:
        resolved_by = get_role_from_token(get_token())
        
        if USE_DATABASE:
            # Database mode
            success = update_evidence_resolution(evidence_id, True, resolved_by)
            if not success:
                return abort(404)
        else:
            # JSON mode
            json_path = os.path.join(EVIDENCE_DIR, f"{evidence_id}.json")
            if not os.path.exists(json_path):
                return abort(404)
            
            with open(json_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            
            meta['resolved'] = True
            meta['resolved_at'] = time.strftime("%Y-%m-%d %H:%M:%S")
            meta['resolved_by'] = resolved_by
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(meta, f, indent=2)
        
        return jsonify({'success': True, 'message': 'Incident marked as resolved'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.post('/evidence/<evidence_id>/unresolve')
@require_role(['admin', 'security'])
def unresolve_evidence(evidence_id):
    """Mark an incident as unresolved"""
    try:
        if USE_DATABASE:
            # Database mode
            success = update_evidence_resolution(evidence_id, False)
            if not success:
                return abort(404)
        else:
            # JSON mode
            json_path = os.path.join(EVIDENCE_DIR, f"{evidence_id}.json")
            if not os.path.exists(json_path):
                return abort(404)
            
            with open(json_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            
            meta['resolved'] = False
            if 'resolved_at' in meta:
                del meta['resolved_at']
            if 'resolved_by' in meta:
                del meta['resolved_by']
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(meta, f, indent=2)
        
        return jsonify({'success': True, 'message': 'Incident marked as unresolved'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.get('/health')
@csrf.exempt
def health():
    return {'status': 'ok'}


# ============================================================================
# Device Management API Endpoints
# ============================================================================

@app.post('/api/devices/pairing-code')
@require_role(['admin'])
def create_pairing_code():
    """Generate a new pairing code for device registration"""
    if not USE_DATABASE:
        return jsonify({'success': False, 'error': 'Device management requires database mode'}), 400
    
    try:
        data = request.get_json() or {}
        role = data.get('role', 'staff')
        expires_minutes = int(data.get('expires_minutes', 10))
        
        # Validate role
        if role not in ['admin', 'security', 'staff', 'viewer']:
            return jsonify({'success': False, 'error': 'Invalid role'}), 400
        
        created_by = get_role_from_token(get_token())
        code = generate_pairing_code(role, created_by, expires_minutes)
        
        if code:
            # Cleanup old expired codes
            cleanup_expired_pairing_codes()
            
            return jsonify({
                'success': True,
                'code': code,
                'role': role,
                'expires_minutes': expires_minutes
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to generate code'}), 500
    except Exception as e:
        logger.error(f"Error creating pairing code: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.post('/api/devices/register')
@csrf.exempt  # Mobile apps won't have CSRF tokens
def register_device_endpoint():
    """Register a new device using a pairing code"""
    if not USE_DATABASE:
        return jsonify({'success': False, 'error': 'Device management requires database mode'}), 400
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        code = data.get('code')
        device_id = data.get('device_id')
        device_name = data.get('device_name', 'Unknown Device')
        device_model = data.get('device_model', 'Unknown')
        device_os = data.get('device_os', 'Unknown')
        
        if not code or not device_id:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Generate auth token for the device
        auth_token = secrets.token_urlsafe(32)
        
        # Get client IP
        ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
        
        # Register device
        success = register_device(
            code=code,
            device_id=device_id,
            device_name=device_name,
            device_model=device_model,
            device_os=device_os,
            auth_token=auth_token,
            ip_address=ip_address,
            metadata=data.get('metadata', {})
        )
        
        if success:
            return jsonify({
                'success': True,
                'auth_token': auth_token,
                'message': 'Device registered successfully'
            })
        else:
            return jsonify({'success': False, 'error': 'Invalid or expired pairing code'}), 400
    except Exception as e:
        logger.error(f"Error registering device: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.post('/api/devices/<device_id>/revoke')
@require_role(['admin'])
def revoke_device_endpoint(device_id):
    """Revoke device access"""
    if not USE_DATABASE:
        return jsonify({'success': False, 'error': 'Device management requires database mode'}), 400
    
    try:
        revoked_by = get_role_from_token(get_token())
        success = revoke_device(device_id, revoked_by)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Device access revoked successfully'
            })
        else:
            return jsonify({'success': False, 'error': 'Device not found'}), 404
    except Exception as e:
        logger.error(f"Error revoking device: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.get('/api/devices')
@require_role(['admin'])
def get_devices_api():
    """Get all devices (API endpoint)"""
    if not USE_DATABASE:
        return jsonify({'success': False, 'error': 'Device management requires database mode'}), 400
    
    try:
        role_filter = request.args.get('role', 'all')
        active_only = request.args.get('active_only', 'false').lower() == 'true'
        
        devices_list = get_all_devices(role_filter, active_only)
        stats = get_device_stats()
        
        return jsonify({
            'success': True,
            'devices': devices_list,
            'stats': stats
        })
    except Exception as e:
        logger.error(f"Error getting devices: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.post('/api/devices/heartbeat')
@csrf.exempt  # Mobile apps won't have CSRF tokens
def device_heartbeat():
    """Update device last seen timestamp"""
    if not USE_DATABASE:
        return jsonify({'success': False, 'error': 'Device management requires database mode'}), 400
    
    try:
        # Get device auth token from header
        auth_token = request.headers.get('X-Device-Token')
        if not auth_token:
            return jsonify({'success': False, 'error': 'No device token provided'}), 401
        
        # Get device by token
        device = get_device_by_token(auth_token)
        if not device:
            return jsonify({'success': False, 'error': 'Invalid device token'}), 401
        
        # Update last seen
        ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
        update_device_last_seen(device['id'], ip_address)
        
        return jsonify({
            'success': True,
            'message': 'Heartbeat received'
        })
    except Exception as e:
        logger.error(f"Error processing heartbeat: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
