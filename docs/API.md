# AutoGuard API Reference

**Version:** 1.0.0  
**Base URL:** `http://localhost:5000` (development)  
**Authentication:** Token-based (Header or Cookie)

---

## Authentication

All protected endpoints require authentication via one of three methods:

### Method 1: Header (Recommended for API clients)
```http
GET /evidence HTTP/1.1
Host: localhost:5000
X-Auth-Token: your_token_here
```

### Method 2: Cookie (Used by web dashboard)
```http
GET /dashboard HTTP/1.1
Host: localhost:5000
Cookie: auth_token=your_token_here
```

### Roles
- **Admin:** Full access to all features
- **Security:** View and manage evidence, no system config
- **Viewer:** Read-only access to dashboard and live feed

---

## Endpoints

### Authentication

#### `POST /login`
Authenticate and set session cookie.

**Request:**
```http
POST /login HTTP/1.1
Content-Type: application/x-www-form-urlencoded

token=your_admin_token_here
```

**Response:**
```http
HTTP/1.1 302 Found
Location: /dashboard
Set-Cookie: auth_token=...; HttpOnly; Secure; SameSite=Strict
```

#### `POST /logout`
Clear authentication cookie.

**Request:**
```http
POST /logout HTTP/1.1
Cookie: auth_token=...
```

**Response:**
```http
HTTP/1.1 302 Found
Location: /
Set-Cookie: auth_token=; expires=Thu, 01 Jan 1970
```

---

### Dashboard

#### `GET /`
Root endpoint - redirects to dashboard or login.

**Auth:** None required  
**Response:** 302 redirect

#### `GET /dashboard`
Main dashboard interface with evidence list.

**Auth:** All roles  
**Query Parameters:**
- `date_range` (optional): `all`, `today`, `week`, `month`
- `rule_type` (optional): `all`, `loitering`, `exit_checkout`, `shelf_exit`, `violence`
- `camera` (optional): `all`, or specific camera ID
- `page` (optional): Page number (default: 1)

**Response:** HTML page

**Example:**
```
GET /dashboard?date_range=today&rule_type=loitering&page=1
```

---

### Evidence Management

#### `GET /evidence`
List all evidence (JSON format).

**Auth:** All roles  
**Rate Limit:** 120 requests/minute

**Response:**
```json
[
  {
    "timestamp": "2026-08-28 03:45:00",
    "person_id": 123,
    "rule": "Loitering in Shelf Zone",
    "camera_id": "CAM01",
    "image_path": "/path/to/evidence_CAM01_id123_Loitering_20260828-034500.jpg",
    "sha256": "a3b2c1...",
    "description": "Person ID 123 remained in the Shelf Area for 8 seconds...",
    "priority": "standard",
    "resolved": false
  }
]
```

#### `GET /evidence/image`
Get specific evidence image.

**Auth:** Admin, Security  
**Rate Limit:** 120 requests/minute  
**Query Parameters:**
- `name` (required): Filename only (no paths)

**Request:**
```
GET /evidence/image?name=evidence_CAM01_id123_Loitering_20260828-034500.jpg
```

**Response:**
- **200 OK:** Image file (JPEG)
- **403 Forbidden:** Invalid filename or unauthorized
- **404 Not Found:** File doesn't exist

#### `GET /evidence/thumb`
Get thumbnail version of evidence image.

**Auth:** All roles  
**Rate Limit:** 240 requests/minute  
**Query Parameters:**
- `name` (required): Original filename

**Request:**
```
GET /evidence/thumb?name=evidence_CAM01_id123_Loitering_20260828-034500.jpg
```

**Response:**
- **200 OK:** Thumbnail image (320px width, JPEG)
- **404 Not Found:** File doesn't exist

#### `GET /evidence/export`
Export all evidence as ZIP file.

**Auth:** Admin, Security  
**Rate Limit:** 30 requests/minute

**Response:**
- **200 OK:** ZIP file download (`autoguard_evidence.zip`)

#### `POST /evidence/<evidence_id>/resolve`
Mark incident as resolved.

**Auth:** Admin, Security  
**Path Parameters:**
- `evidence_id`: Evidence filename without extension

**Response:**
```json
{
  "success": true,
  "message": "Incident marked as resolved"
}
```

**Metadata Updated:**
```json
{
  "resolved": true,
  "resolved_at": "2026-08-28 03:45:00",
  "resolved_by": "admin"
}
```

#### `POST /evidence/<evidence_id>/unresolve`
Mark incident as unresolved.

**Auth:** Admin, Security  
**Response:**
```json
{
  "success": true,
  "message": "Incident marked as unresolved"
}
```

---

### Live Feed

#### `GET /live`
Live video feed interface.

**Auth:** All roles  
**Response:** HTML page with video player

#### `GET /video_feed`
Video streaming endpoint (multipart/x-mixed-replace).

**Auth:** All roles  
**Response:** MJPEG stream (~30 FPS)

**Usage:**
```html
<img src="/video_feed" alt="Live Feed">
```

#### `GET /stream_stats`
Get streaming statistics.

**Auth:** All roles  
**Response:**
```json
{
  "active_clients": 2,
  "fps": 29.8,
  "frame_count": 15432,
  "uptime_seconds": 517
}
```

#### `GET /live_activity`
Get live activity statistics and recent detections.

**Auth:** All roles  
**Response:**
```json
{
  "activity": {
    "total_detections": 42,
    "active_persons": 3,
    "alerts_triggered": 5
  },
  "recent_detections": [
    {
      "person_id": 123,
      "zone": "shelf",
      "timestamp": "2026-08-28T03:45:00Z",
      "rule_triggered": null
    }
  ],
  "system": {
    "cpu_percent": 45.2,
    "memory_gb": 2.3,
    "memory_percent": 28.7
  }
}
```

#### `GET /snapshot`
Capture single frame snapshot from live feed.

**Auth:** All roles  
**Response:**
- **200 OK:** JPEG image download
- **404 Not Found:** No frame available

**Filename format:** `snapshot_CAM01_20260828-034500.jpg`

---

### System

#### `GET /health`
Health check endpoint (no auth required).

**Auth:** None  
**Response:**
```json
{
  "status": "ok"
}
```

#### `GET /whoami`
Check current authentication role.

**Auth:** None (returns anonymous if not authenticated)  
**Response:**
```json
{
  "role": "admin"
}
```

#### `GET /devices`
Device management interface.

**Auth:** Admin only  
**Response:** HTML page

#### `GET /config`
Configuration interface (placeholder).

**Auth:** Admin only  
**Response:** HTML page

---

## Error Responses

### Standard Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid parameters |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |

### Error Response Format
```json
{
  "success": false,
  "error": "Error description here"
}
```

---

## Rate Limiting

Rate limits are per-IP address per endpoint:

| Endpoint | Limit |
|----------|-------|
| `/evidence` | 120/min |
| `/evidence/image` | 120/min |
| `/evidence/thumb` | 240/min |
| `/evidence/export` | 30/min |
| `/dashboard` | 60/min |
| Other endpoints | No limit |

**Rate Limit Response:**
```http
HTTP/1.1 429 Too Many Requests
```

---

## Webhook Integration (Future)

### Telegram Bot
Configure in `.env`:
```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_IDS=123456789,987654321
```

Alerts sent automatically on rule triggers.

---

## Code Examples

### Python
```python
import requests

# Authentication
base_url = "http://localhost:5000"
token = "your_admin_token_here"
headers = {"X-Auth-Token": token}

# List evidence
response = requests.get(f"{base_url}/evidence", headers=headers)
evidence = response.json()

# Download image
image_name = "evidence_CAM01_id123_Loitering_20260828-034500.jpg"
response = requests.get(
    f"{base_url}/evidence/image",
    headers=headers,
    params={"name": image_name}
)
with open("download.jpg", "wb") as f:
    f.write(response.content)

# Mark resolved
evidence_id = "evidence_CAM01_id123_Loitering_20260828-034500"
response = requests.post(
    f"{base_url}/evidence/{evidence_id}/resolve",
    headers=headers
)
print(response.json())
```

### JavaScript
```javascript
// Authentication via cookie (handled by browser)
const baseUrl = 'http://localhost:5000';

// Fetch evidence list
fetch(`${baseUrl}/evidence`)
  .then(response => response.json())
  .then(evidence => console.log(evidence));

// Mark as resolved
fetch(`${baseUrl}/evidence/${evidenceId}/resolve`, {
  method: 'POST'
})
  .then(response => response.json())
  .then(data => console.log(data));
```

### cURL
```bash
# Login
curl -X POST http://localhost:5000/login \
  -d "token=your_token_here" \
  -c cookies.txt

# List evidence
curl -b cookies.txt http://localhost:5000/evidence

# Download image
curl -b cookies.txt \
  "http://localhost:5000/evidence/image?name=evidence_CAM01_id123.jpg" \
  -o downloaded.jpg

# Export all evidence
curl -b cookies.txt \
  http://localhost:5000/evidence/export \
  -o evidence_export.zip
```

---

## WebSocket Support (Future Enhancement)

Real-time updates via WebSocket:
```javascript
const ws = new WebSocket('ws://localhost:5000/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'new_evidence') {
    console.log('New detection:', data.evidence);
  }
};
```

---

**Document Version:** 1.0  
**Last Updated:** August 28, 2026
