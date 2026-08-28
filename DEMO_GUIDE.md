# AutoGuard Demo Guide for Professor

## Quick Start

### Step 1: Start Detection System
```bash
start.bat
```
This launches the camera feed with AI detection. You'll see:
- ✅ Live video feed from your webcam
- ✅ Zone overlays (Shelf=Yellow, Checkout=Magenta, Exit=Cyan)
- ✅ Person detection boxes with Track IDs
- ✅ Real-time status: "CAM: CAM01 | Frame: X | LIVE"
- ✅ Timestamp overlay

### Step 2: Start Web Dashboard
```bash
start_dashboard.bat
```
This launches the web interface at `http://localhost:5000`

### Step 3: Login to Dashboard
1. Open browser: `http://localhost:5000/login`
2. Enter token from `.env` file:
   - `ADMIN_TOKEN` - Full access (can mark incidents as resolved)
   - `SECURITY_TOKEN` - Security staff access
   - `VIEWER_TOKEN` - Read-only access

---

## Dashboard Features

### 1. Evidence Dashboard (`/dashboard`)
**Real-time Incident Monitoring**

#### Statistics Cards (Top Row):
- **Total Incidents** - All detected violations
- **High Priority** - Violence/threat incidents
- **Theft Alerts** - Standard priority incidents (loitering, exit without checkout)
- **Resolved** - Incidents marked as handled

#### Working Filters:
- **Date Range**: Today, Last 7 Days, Last 30 Days, All Time
- **Rule Type**: Filter by specific violation types
  - Loitering in Shelf Zone
  - Exit Without Checkout
  - Repeated Shelf-Exit Movement
  - Violence/Threat
- **Camera**: Filter by camera ID (CAM01, etc.)

#### Incident Cards Show:
- Evidence snapshot image
- Priority badge (HIGH PRIORITY or STANDARD)
- Resolved status badge (if marked as resolved)
- Camera ID and Track ID
- AI-generated description of the incident
- Timestamp
- Action buttons:
  - **Mark Resolved** / **Unresolve** (for admin/security roles)
  - **Download** evidence image

#### Features:
- ✅ Auto-refreshes every 30 seconds
- ✅ Pagination (12 incidents per page)
- ✅ Click image to view full-size
- ✅ Filter results preserved across pages

---

### 2. Live Feed Page (`/live`)
**Real-time Video Stream with Overlays**

#### Main Video Display:
- **Live camera feed** streamed from detection system
- Shows same view as the detection window but accessible via web
- Includes all detection overlays:
  - Person bounding boxes
  - Track IDs
  - Zone boundaries
  - Detection status

#### Connection Status:
- **Green "Connected"** - Stream is active and receiving frames
- **Orange "No Feed"** - Detection system not running
- **Red "Disconnected"** - Connection lost (auto-reconnect)

#### Features:
- ✅ Real-time streaming (~30 FPS)
- ✅ Automatic reconnection if feed drops
- ✅ Status monitoring every 3 seconds

---

## Detection Rules & Behavior

### Rule 1: Loitering in Shelf Zone
**Triggers when:** Person stays in shelf area for ≥5 seconds
- **Priority:** Standard
- **Audio Alert:** Beep sound (if enabled)
- **Behavior:** Continuously alerts every 5 seconds while loitering

### Rule 2: Exit Without Checkout
**Triggers when:** Person visits shelf zone but exits without visiting checkout
- **Priority:** Standard
- **Audio Alert:** Beep sound (if enabled)
- **Evidence:** Captures when person enters exit zone

### Rule 3: Repeated Shelf-Exit Movement
**Triggers when:** Person moves between shelf and exit zones 2+ times in 60 seconds
- **Priority:** Standard
- **Indicates:** Suspicious back-and-forth behavior

### Rule 4: Violence/Threat Detection
**Triggers when:** Violence-related keywords detected (future expansion)
- **Priority:** HIGH
- **Immediate alert:** Highest priority notification

---

## AI-Generated Descriptions

Each incident includes an AI-generated description with context:

**Example for Loitering:**
> "Individual with Track ID 15 detected loitering in shelf zone for 8.2 seconds. Subject remained in merchandise area beyond normal browsing time. Camera CAM01 recorded this activity at 2026-08-26 18:30:45."

**Example for Exit Without Checkout:**
> "Track ID 23 visited shelf area but proceeded directly to exit zone without passing through checkout. Potential theft behavior detected by Camera CAM01 at 2026-08-26 18:32:10."

---

## Evidence Management

### Evidence Storage
- Location: `evidence/` directory
- Each incident creates:
  - `.jpg` - Snapshot image with detection box
  - `.json` - Metadata (rule, timestamp, track ID, camera, description, priority)

### Evidence Export
- Download individual images from dashboard
- Bulk export: `/evidence/export` (creates ZIP with all evidence)

### Retention Policy
- Configurable in `config/config.yaml`
- Default: 7 days
- Old evidence automatically deleted on system start

---

## System Architecture

### Detection System (`start.bat`)
1. Opens camera (index 1 - your webcam)
2. Runs YOLOv8n for person detection
3. Tracks persons with ByteTrack
4. Monitors zone transitions
5. Evaluates behavior rules
6. Captures evidence when rules trigger
7. **Streams frames to web dashboard**
8. Sends Telegram alerts (if configured)

### Web Dashboard (`start_dashboard.bat`)
1. Flask web server on port 5000
2. Token-based authentication (3 role levels)
3. Evidence management API
4. Video streaming endpoint
5. Real-time statistics
6. Incident resolution tracking

### Stream Manager (New!)
- Shared memory buffer between detection and web server
- Detection system pushes frames every cycle
- Web dashboard pulls frames for streaming
- Multiple clients supported
- Automatic reconnection handling

---

## Professor Demo Flow

### Scenario 1: Normal Shopping Behavior
1. Stand in front of camera
2. Move through shelf → checkout → exit zones
3. Show that no alerts are triggered
4. Dashboard shows no incidents

### Scenario 2: Loitering Detection
1. Stand in shelf zone (yellow box)
2. Wait for 5+ seconds without moving
3. Beep will sound
4. Evidence captured automatically
5. Refresh dashboard to see new incident
6. Show AI description
7. Mark incident as "Resolved"

### Scenario 3: Exit Without Checkout
1. Move to shelf zone
2. Skip checkout zone
3. Go directly to exit zone
4. Beep will sound
5. Evidence captured
6. Dashboard shows "Exit Without Checkout" incident

### Scenario 4: Live Feed Demo
1. Open `/live` page on dashboard
2. Show real-time video stream
3. Move around to demonstrate detection
4. Point out zone overlays and detection boxes
5. Show connection status indicator

### Scenario 5: Filter & Search
1. Generate multiple incidents (different types)
2. Use date filter to show "Today" vs "All Time"
3. Filter by rule type (Loitering only, Exit only)
4. Show pagination when >12 incidents
5. Demonstrate resolved vs unresolved filtering

---

## Technical Highlights for Professor

### 1. Computer Vision
- **YOLOv8n** - State-of-the-art object detection
- **ByteTrack** - Multi-object tracking
- **Zone-based monitoring** - Custom behavior analysis

### 2. Real-time Processing
- ~24 FPS detection rate
- <50ms latency per frame
- Concurrent video display and web streaming

### 3. Web Dashboard
- **Flask** backend with RESTful API
- **Token-based RBAC** (Role-Based Access Control)
- **MJPEG streaming** for live video
- **Auto-refresh** for real-time updates

### 4. Evidence Management
- Automatic snapshot capture
- AI-generated descriptions
- JSON metadata storage
- Configurable retention policy

### 5. Alert System
- Multiple alert channels (Beep, Telegram)
- Cooldown and daily cap to prevent spam
- Priority-based routing

---

## Troubleshooting

### Camera shows black screen
- Other apps might be using camera (close Zoom, Teams, etc.)
- Check logs in `logs/` directory
- System automatically tries camera indices 1, 0, 2

### Dashboard shows "No incidents"
- Detection system needs to be running (`start.bat`)
- Trigger a rule by loitering in shelf zone
- Check `evidence/` folder for files

### Live feed shows "No Feed"
- Start detection system first (`start.bat`)
- Wait 2-3 seconds for stream manager to initialize
- Check connection status indicator

### Login issues
- Check `.env` file for tokens
- Default tokens should be set
- Use ADMIN_TOKEN for full access

---

## Configuration Files

### `config/config.yaml`
- Camera settings (source, resolution)
- Detection confidence threshold
- Rule parameters (loitering time, repeat counts)
- Alert settings (cooldown, daily cap)
- Zone coordinates

### `.env`
- Authentication tokens (ADMIN_TOKEN, SECURITY_TOKEN, VIEWER_TOKEN)
- Telegram bot credentials (optional)

---

## What's Working (Summary)

✅ **Camera Detection** - Real-time person detection and tracking  
✅ **Zone Monitoring** - Shelf, checkout, exit zones  
✅ **Behavior Rules** - Loitering, exit without checkout, repeated movements  
✅ **Evidence Capture** - Automatic snapshots with metadata  
✅ **AI Descriptions** - Context-aware incident descriptions  
✅ **Web Dashboard** - Real-time monitoring interface  
✅ **Live Video Stream** - Web-based camera feed  
✅ **Filters & Search** - Date, rule type, camera filters  
✅ **Pagination** - Navigate through multiple incidents  
✅ **Incident Resolution** - Mark incidents as resolved/unresolved  
✅ **Priority System** - High priority for violence, standard for theft  
✅ **Authentication** - Role-based access control  
✅ **Auto-refresh** - Dashboard updates every 30 seconds  
✅ **Audio Alerts** - Beep notifications for rules  
✅ **Export** - Download evidence images  

---

## Future Enhancements (Optional Discussion)

- Multi-camera support
- Advanced pose detection for violence/aggression
- Heatmap visualization of high-traffic areas
- Mobile app for security staff
- Integration with POS systems
- Facial recognition (with privacy controls)
- Report generation (daily/weekly summaries)

---

## Contact & Support

For issues or questions during demo:
1. Check logs in `logs/` directory
2. Verify camera index in config
3. Ensure both start.bat scripts are running
4. Check browser console for errors (F12)

**System Requirements:**
- Python 3.8+
- Webcam (camera index 1)
- Windows OS (for audio alerts)
- Modern web browser (Chrome, Firefox, Edge)

---

## Quick Commands Reference

```bash
# Start detection system
start.bat

# Start web dashboard
start_dashboard.bat

# Test camera
python test_camera.py

# View logs
type logs\autoguard_*.log
```

**Dashboard URLs:**
- Login: `http://localhost:5000/login`
- Dashboard: `http://localhost:5000/dashboard`
- Live Feed: `http://localhost:5000/live`

---

Good luck with your demo! 🚀
