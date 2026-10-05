# AutoGuard v1.1.0 - Quick Start Guide

## What's New in v1.1.0 (September 26, 2026)

### 🔒 CSRF Protection
- Added Flask-WTF for Cross-Site Request Forgery protection
- All POST endpoints now validate CSRF tokens
- Professional login page with secure authentication
- Enhanced security headers

### 💾 Database Integration
- SQLite database support for evidence metadata
- Backward compatible with JSON file storage
- Fast querying with optimized indexes
- Migration tool to import existing evidence

### 📹 RTSP Stream Support
- Support for IP cameras and network streams
- RTSP, RTMP, HTTP, and MJPEG protocols
- Automatic reconnection for network streams
- Video file playback support

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Video Source

**Option A: USB Camera (Default)**
```yaml
# config/config.yaml
video:
  source: 0  # Camera index
```

**Option B: RTSP IP Camera**
```yaml
# config/config.yaml
video:
  source: "rtsp://admin:password@192.168.1.100:554/stream"
  reconnect_delay: 5
  max_reconnect_attempts: 10
```

**Option C: Video File**
```yaml
# config/config.yaml
video:
  source: "test_video.mp4"
```

### 3. Enable CSRF Protection

Generate a secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Add to `.env`:
```bash
FLASK_SECRET_KEY=your_generated_secret_key_here
```

### 4. Enable Database (Optional)

**Migrate existing evidence:**
```bash
python migrate_to_database.py
```

**Enable database mode in `.env`:**
```bash
USE_DATABASE=true
```

### 5. Start AutoGuard

**Detection Engine:**
```bash
start_detection.bat
# or
python -m src.main --source 0
```

**Web Dashboard:**
```bash
start_dashboard.bat
# or
python -m src.server
```

---

## Testing RTSP Streams

Test your RTSP connection before using:

```bash
python test_rtsp.py "rtsp://admin:password@192.168.1.100:554/stream"
```

Test USB camera:
```bash
python test_rtsp.py 0
```

---

## Configuration Examples

### Example 1: USB Camera with Database

```yaml
# config/config.yaml
video:
  source: 0
  width: 1280
  height: 720
  display: true
```

```bash
# .env
USE_DATABASE=true
FLASK_SECRET_KEY=1038ec04186235219b5efdf1b6a989d2542f35f2f27b16689a357beda4049e33
ADMIN_TOKEN=your_admin_token
SECURITY_TOKEN=your_security_token
VIEWER_TOKEN=your_viewer_token
```

### Example 2: Hikvision IP Camera

```yaml
# config/config.yaml
video:
  source: "rtsp://admin:Camera123@192.168.1.64:554/Streaming/Channels/101"
  reconnect_delay: 5
  max_reconnect_attempts: 10
  display: true

alerts:
  camera_id: "ENTRANCE_CAM"
  enabled: true
```

### Example 3: Multiple Sources (Manual Switch)

**For Entrance Camera:**
```yaml
video:
  source: "rtsp://192.168.1.100:554/entrance"
alerts:
  camera_id: "ENTRANCE"
```

**For Checkout Camera:**
```yaml
video:
  source: "rtsp://192.168.1.101:554/checkout"
alerts:
  camera_id: "CHECKOUT"
```

---

## Common RTSP URLs

### Hikvision
```
rtsp://admin:password@192.168.1.64:554/Streaming/Channels/101
```

### Dahua
```
rtsp://admin:password@192.168.1.108:554/cam/realmonitor?channel=1&subtype=0
```

### Reolink
```
rtsp://admin:password@192.168.1.100:554/h264Preview_01_main
```

### Foscam
```
rtsp://admin:password@192.168.1.100:554/videoMain
```

### TP-Link
```
rtsp://admin:password@192.168.1.100:554/stream1
```

---

## Troubleshooting

### CSRF Token Missing

**Error:** "CSRF token missing"

**Solution:**
1. Clear browser cookies
2. Ensure `FLASK_SECRET_KEY` is set in `.env`
3. Restart the dashboard server

### RTSP Connection Failed

**Error:** "Failed to connect to RTSP source"

**Solution:**
1. Test with VLC Media Player first
2. Verify IP address, port, username, password
3. Check camera RTSP is enabled
4. Use `test_rtsp.py` to diagnose

```bash
python test_rtsp.py "rtsp://your-camera-url"
```

### Database Migration Issues

**Error:** During migration

**Solution:**
1. Backup is automatically created in `evidence/json_backup/`
2. Check logs for specific errors
3. Ensure SQLite is available (built into Python)

### Video Stream Freezes

**Solution:**
1. Use sub-stream (lower resolution)
2. Increase reconnection attempts
3. Check network stability
4. Use wired connection instead of WiFi

---

## Environment Variables

```bash
# .env file

# Flask Configuration
FLASK_SECRET_KEY=generated_secret_key_here

# Database Mode
USE_DATABASE=true  # or false for JSON mode

# Authentication Tokens
ADMIN_TOKEN=secure_admin_token
SECURITY_TOKEN=secure_security_token
VIEWER_TOKEN=secure_viewer_token

# Telegram Alerts (Optional)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_IDS=123456789,987654321

# Camera ID
CAMERA_ID=CAM01
```

---

## Command Line Options

```bash
# Start with specific camera
python -m src.main --source 0

# Start with RTSP stream
python -m src.main --source "rtsp://camera-url"

# Start with video file
python -m src.main --source "video.mp4"

# Start with custom config
python -m src.main --config custom_config.yaml
```

---

## Web Dashboard

### Access
```
http://localhost:5000
```

### Login
Use one of the tokens from `.env`:
- **Admin:** Full access
- **Security:** Evidence management
- **Viewer:** Read-only access

### Features
- Real-time live feed
- Evidence gallery with filtering
- Incident resolution tracking
- Statistics dashboard
- Evidence export (ZIP)

---

## File Structure

```
Major Project/
├── config/
│   └── config.yaml          # Main configuration
├── src/
│   ├── main.py              # Detection engine
│   ├── server.py            # Web dashboard
│   ├── database.py          # SQLite database (NEW)
│   ├── video_source.py      # Video source manager (NEW)
│   └── ...
├── data/
│   └── autoguard.db         # SQLite database (created)
├── evidence/
│   ├── *.jpg                # Evidence images
│   ├── *.json               # Evidence metadata (legacy)
│   └── json_backup/         # Backup of JSON files
├── templates/
│   ├── login.html           # Login page (NEW)
│   └── ...
├── .env                     # Environment variables
├── requirements.txt         # Python dependencies
├── test_rtsp.py            # RTSP test utility (NEW)
├── migrate_to_database.py  # Database migration tool (NEW)
├── RTSP_GUIDE.md           # RTSP configuration guide (NEW)
└── README.md                # Main documentation
```

---

## Performance Tips

### For USB Cameras
```yaml
video:
  source: 0
  width: 1280
  height: 720
  buffer_size: 1  # Minimize latency
```

### For RTSP Streams
```yaml
video:
  source: "rtsp://camera/sub_stream"  # Use sub-stream for better performance
  reconnect_delay: 3
  max_reconnect_attempts: 20
```

### Database Mode
- Faster queries with large evidence datasets
- Better filtering and searching
- Reduced disk I/O

---

## Security Recommendations

1. **Use strong tokens** in `.env`
2. **Enable HTTPS** for production (nginx/Apache)
3. **Don't expose RTSP** ports to internet
4. **Use VPN** for remote access
5. **Change default camera passwords**
6. **Regular security updates**

---

## Getting Help

- **Main Documentation:** `README.md`
- **RTSP Guide:** `RTSP_GUIDE.md`
- **Security Guide:** `docs/SECURITY.md`
- **API Reference:** `docs/API.md`

---

## Version Compatibility

- **Python:** 3.10+
- **OpenCV:** 4.9.0+
- **Flask:** 3.0.0+
- **CUDA (Optional):** For GPU acceleration

---

## Known Limitations

- Single camera support (multi-camera in v1.5)
- No live dashboard updates (WebSocket in v1.2)
- Basic search (advanced search in v1.2)

---

## Next Steps

1. ✅ Test your video source
2. ✅ Configure `.env` file
3. ✅ Calibrate detection zones
4. ✅ Test alert system
5. ✅ Monitor for false positives
6. ✅ Adjust confidence thresholds

---

**AutoGuard v1.1.0** - September 26, 2026  
**Status:** Production Ready ✅
