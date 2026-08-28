# Dashboard Module – Web Security Dashboard

**Module:** Web Dashboard (Manager/Owner Interface)  
**Status:** ⚠️ Very basic Flask viewer only (~15% complete)  
**Last Updated:** 2026-08-26  
**Owner:** Cybersecurity Final Year Project Team

---

## Purpose

The Web Dashboard is the primary interface for store managers and owners to monitor the AutoGuard system. It provides live camera views, incident review, evidence management, device pairing controls, and system configuration.

**Key Responsibilities:**
- Display live camera feed with detection overlays
- Show incident timeline (chronological list of rule triggers)
- Provide evidence viewer with download/export capabilities
- Manage paired mobile devices (list, generate pairing codes, revoke access)
- Configure detection rules and thresholds
- Display analytics and system health metrics
- Enforce manager-only access controls

---

## Architecture

```
Browser
  ↓ HTTPS (planned)
Web Dashboard (React/Vue planned, or enhanced Flask templates)
  ↓ REST API + WebSocket
Backend API (Flask → FastAPI)
  ↓
Evidence Storage + Database + Live Camera Feed
```

**Current State:** Basic Flask app serving static HTML with evidence thumbnails. No live feed, no device management, no configuration UI.

---

## Current Implementation

**File:** `src/server.py` (Flask application)

### Existing Endpoints

**`GET /`**
- Simple HTML instructions page
- Lists available endpoints
- No authentication required

**`GET /evidence`**
- Returns JSON array of all evidence files
- Scans `evidence/` directory for .jpg + .json pairs
- **Response Example:**
```json
[
  {
    "image": "CAM01_20260826_102340_ID42.jpg",
    "metadata": "CAM01_20260826_102340_ID42.json",
    "timestamp": "2026-08-26T10:23:40Z",
    "rule": "Loitering in Shelf Zone",
    "camera_id": "CAM01",
    "track_id": 42
  }
]
```

**`GET /evidence/image?path=<filename>`**
- Serves evidence image file
- **Query Parameters:** `path` (filename only)
- **Response:** JPEG image with Content-Type: image/jpeg
- ⚠️ **Security Issue:** No path sanitization (vulnerable to directory traversal)

**`GET /dashboard`**
- HTML page with evidence thumbnails in 3-column grid
- Shows: thumbnail image, rule name, timestamp
- Click thumbnail to view full-size image
- Basic CSS styling (inline)
- **Status:** Works but very basic UI

### Authentication (Current)

Optional role-based tokens via environment variables:
```bash
ADMIN_TOKEN=secure_admin_token
SECURITY_TOKEN=secure_security_token
VIEWER_TOKEN=secure_viewer_token
```

- Checked via `Authorization: Bearer <token>` header
- No enforcement on most endpoints (demo-only implementation)
- **Status:** ⚠️ Placeholder, not production-ready

---

## Planned Features (Week 8)

### 1. Live Camera View
**Status:** ❌ Not implemented

**Requirements:**
- Real-time video stream from active camera
- Detection overlays (bounding boxes, track IDs, zones)
- Smooth playback (target: 15-25 FPS)

**Technical Approach:**
- **Option A:** MJPEG stream over HTTP (simple, good browser support)
- **Option B:** HLS (HTTP Live Streaming) for better quality/buffering
- **Option C:** WebRTC for lowest latency (more complex)

**Recommendation:** Start with MJPEG over WebSocket (easiest to implement)

**Implementation Plan:**
```python
# Backend: WebSocket endpoint streaming MJPEG frames
@app.websocket('/api/live')
async def live_feed(websocket):
    # Capture frames from camera
    # Encode as JPEG
    # Send over WebSocket
    pass

# Frontend: Display in <img> or <video> tag
```

---

### 2. Incident Timeline
**Status:** ❌ Not implemented

**Requirements:**
- Chronological list of all rule triggers (newest first)
- Filter by: date range, camera, rule type, severity
- Pagination (20-50 incidents per page)
- Visual severity indicators (color-coded: standard vs high-priority)

**UI Mockup:**
```
┌─────────────────────────────────────────────────────┐
│ Filters: [Date] [Camera] [Rule] [Severity] [Search]│
├─────────────────────────────────────────────────────┤
│ 🔴 HIGH PRIORITY | 10:34:21 | CAM01 | Track ID 42  │
│    Aggressive Pose Detection                        │
│    [Thumbnail] [View Details] [Mark False Positive] │
├─────────────────────────────────────────────────────┤
│ 🟡 STANDARD | 10:23:40 | CAM01 | Track ID 42       │
│    Loitering in Shelf Zone (52 seconds)            │
│    [Thumbnail] [View Details] [Mark Resolved]      │
└─────────────────────────────────────────────────────┘
```

---

### 3. Evidence Management
**Status:** ⚠️ Basic viewer only

**Current:** Thumbnail grid, full-size view  
**Missing:**
- Incident detail view (full metadata, AI description, zone info)
- Evidence export (ZIP download with integrity manifest)
- Evidence retention management (manual delete, retention policy)
- Search/filter evidence by metadata
- Mark as resolved / false positive / escalated

**Planned Detail View:**
```
┌──────────────────────────────────────────────────────┐
│ Incident Details                                     │
├──────────────────────────────────────────────────────┤
│ [Full-size Evidence Image]                           │
│                                                      │
│ Rule: Loitering in Shelf Zone                       │
│ AI Description: Person ID 42 remained in electronics│
│   aisle for 52 seconds with repeated hand-to-pocket │
│   motion; flagged as possible concealment behavior. │
│                                                      │
│ Timestamp: 2026-08-26 10:23:40 UTC                  │
│ Camera: CAM01 (Front Store)                         │
│ Track ID: 42                                        │
│ Zone: Shelf                                         │
│ Bounding Box: [120, 340, 280, 650]                 │
│ SHA-256: abc123...def789 ✓ Verified                │
│                                                      │
│ Actions:                                            │
│ [Mark Resolved] [Mark False Positive] [Export]     │
│ [Delete] (requires confirmation)                    │
│                                                      │
│ Notes: (manager can add investigation notes)        │
└──────────────────────────────────────────────────────┘
```

---

### 4. Device Management UI
**Status:** ❌ Not implemented (pairing service not built yet)

**Requirements:**
- List all paired mobile devices
  - Device ID, last seen timestamp, role (staff/security)
  - Active/inactive status
- Generate new pairing code button
  - Display 6-digit code prominently
  - Show expiry countdown (10 minutes)
  - Copy-to-clipboard functionality
- Revoke device access button
  - Confirmation dialog ("Are you sure? Device will stop receiving alerts.")
  - Immediate JWT invalidation

**UI Mockup:**
```
┌──────────────────────────────────────────────────────┐
│ Paired Devices                         [+ Add Device]│
├──────────────────────────────────────────────────────┤
│ 📱 Device #1234 | Staff | Last seen: 2 min ago      │
│    Paired: 2026-08-20 | Status: Active              │
│    [Revoke Access]                                  │
├──────────────────────────────────────────────────────┤
│ 📱 Device #5678 | Security | Last seen: 15 min ago  │
│    Paired: 2026-08-19 | Status: Active              │
│    [Revoke Access]                                  │
└──────────────────────────────────────────────────────┘

[+ Add Device] clicked:
┌──────────────────────────────────────────────────────┐
│ Add New Device                                       │
├──────────────────────────────────────────────────────┤
│ Share this code with the staff member:              │
│                                                      │
│            ┌─────────┐                               │
│            │ 7 3 8 2 │  (larger font, centered)     │
│            └─────────┘                               │
│                                                      │
│ Expires in: 09:42  [Copy Code]                      │
│                                                      │
│ Staff should open the AutoGuard mobile app and      │
│ enter this code under "Join a Store."               │
│                                                      │
│ Code is single-use and expires in 10 minutes.       │
│                                                      │
│ [Close]                                             │
└──────────────────────────────────────────────────────┘
```

---

### 5. Rule Configuration UI
**Status:** ❌ Not implemented

**Requirements:**
- Display current rule thresholds (editable)
- Enable/disable individual rules via toggle switches
- Zone coordinate editor (visual or numeric)
- Save changes with confirmation
- Test rule button (upload video, see if rule would trigger)

**UI Mockup:**
```
┌──────────────────────────────────────────────────────┐
│ Detection Rules Configuration                        │
├──────────────────────────────────────────────────────┤
│ Theft Detection Rules                                │
│                                                      │
│ ☑ Loitering in Shelf Zone                           │
│   Threshold: [5] seconds (slider or input)          │
│   Current: 5s (DEMO - recommend 30-60s production)  │
│                                                      │
│ ☑ Repeated Shelf-Exit Movement                      │
│   Repeat count: [2] times                           │
│   Time window: [60] seconds                         │
│                                                      │
│ ☑ Exit Without Checkout                             │
│   (No threshold - binary rule)                      │
│                                                      │
├──────────────────────────────────────────────────────┤
│ Violence/Threat Detection Rules                     │
│                                                      │
│ ☑ Aggressive Pose Detection                         │
│   Sensitivity: [Medium ▼] (Low/Medium/High)         │
│                                                      │
│ ☑ Rapid Clustering/Dispersal                        │
│   Min people: [3]  Velocity threshold: [1.5] m/s    │
│                                                      │
│ ☑ Elevated Object Detection                         │
│   Confidence threshold: [0.6] (0.0-1.0)             │
│                                                      │
│ ☑ Group Freeze Posture                              │
│   Duration: [3] seconds  Min people: [2]            │
│                                                      │
├──────────────────────────────────────────────────────┤
│ [Save Changes] [Reset to Defaults] [Test Rules]     │
└──────────────────────────────────────────────────────┘
```

---

### 6. Analytics Dashboard
**Status:** ❌ Not implemented

**Requirements:**
- Daily/weekly/monthly incident statistics
- Incident breakdown by rule type (pie chart)
- Incident count over time (line chart)
- Busiest zones heatmap
- False positive rate (if incidents marked as false alarm)
- System uptime and health metrics

**Planned Visualizations:**
- **Chart.js** or **Recharts** for React
- **Plotly** for interactive charts

**Example Metrics:**
```
┌──────────────────────────────────────────────────────┐
│ Analytics Dashboard                                  │
├──────────────────────────────────────────────────────┤
│ Today: 23 incidents | Week: 142 incidents           │
│ False Positive Rate: 12% (17/142)                   │
│ System Uptime: 99.2% (7d 21h)                       │
├──────────────────────────────────────────────────────┤
│ Incidents by Rule Type (Today)                      │
│ [Pie Chart]                                         │
│   - Loitering: 15 (65%)                             │
│   - Exit Without Checkout: 6 (26%)                  │
│   - Repeated Shelf-Exit: 2 (9%)                     │
├──────────────────────────────────────────────────────┤
│ Incident Trend (Last 7 Days)                        │
│ [Line Chart]                                        │
│   Peak: Tuesday 10-11 AM (18 incidents)            │
├──────────────────────────────────────────────────────┤
│ Busiest Zones                                       │
│   1. Shelf Zone: 89 incidents                       │
│   2. Exit Zone: 38 incidents                        │
│   3. Checkout Zone: 15 incidents                    │
└──────────────────────────────────────────────────────┘
```

---

## Technology Stack Options

### Current: Flask + Basic HTML
**Status:** Working but very limited

**Pros:**
- Simple, works for demo
- No build step needed

**Cons:**
- No modern UI framework
- No reactive data binding
- Hard to maintain complex UI

---

### Option A: Enhanced Flask + Jinja Templates
**Effort:** Low (1-2 days)  
**Recommendation:** ⭐ Good for quick demo polish

**Tech:**
- Flask backend (keep existing)
- Jinja2 templates
- Bootstrap 5 CSS framework
- Vanilla JavaScript or jQuery for interactivity

**Pros:**
- Minimal changes to existing Flask app
- Bootstrap provides good-looking components quickly
- No build tooling needed

**Cons:**
- Still limited compared to modern frameworks
- Manual DOM manipulation can get messy
- No component reusability

---

### Option B: FastAPI + React SPA
**Effort:** High (1-2 weeks)  
**Recommendation:** ⭐⭐⭐ Best for production-quality MVP

**Tech:**
- FastAPI backend (migrate from Flask)
- React frontend (Create React App or Vite)
- Material-UI or Ant Design component library
- Axios for API calls
- React Router for navigation
- WebSocket for live feed

**Pros:**
- Modern, professional UI
- Component-based architecture
- Rich ecosystem (charts, tables, forms)
- Built-in dev server with hot reload

**Cons:**
- Significant migration effort
- Requires build step (npm, webpack)
- Steeper learning curve if unfamiliar with React

---

### Option C: FastAPI + Vue.js
**Effort:** High (1-2 weeks)  
**Recommendation:** ⭐⭐ Alternative to React, gentler learning curve

**Tech:**
- FastAPI backend
- Vue 3 frontend (Vite)
- Vuetify or Element Plus component library
- Axios for API calls

**Pros:**
- Simpler than React for beginners
- Good documentation
- Two-way data binding (easier forms)

**Cons:**
- Smaller ecosystem than React
- Still requires build tooling

---

## Recommended Approach for Mock Interview

**Given time constraints, recommend Option A: Enhanced Flask + Bootstrap**

**3-4 Hour Implementation Plan:**

1. **Install Bootstrap 5** (CDN link in HTML, no install needed)
2. **Create professional layout:**
   - Top navbar with AutoGuard logo, navigation links
   - Sidebar for filters/settings
   - Main content area for incident cards
3. **Improve evidence viewer:**
   - Bootstrap cards for evidence thumbnails
   - Modal for full-size view with metadata
   - Badge for rule severity (red for high-priority, yellow for standard)
4. **Add mock live feed:**
   - Placeholder video element or looping GIF
   - Overlay with "LIVE" badge and FPS counter
5. **Add mock device management:**
   - Static table with fake paired devices
   - Modal for "Add Device" with randomly generated 6-digit code
6. **Polish:**
   - Consistent color scheme (security theme: dark blue/cyan)
   - Icons (Bootstrap Icons or Font Awesome)
   - Responsive layout (works on mobile)

**Result:** Professional-looking dashboard that demonstrates the concept, even if full functionality not implemented yet.

---

## Key File Paths

```
src/server.py                    # Flask application (current)
templates/                       # Jinja2 templates (if using Flask + templates)
  ├── base.html                  # Base layout template
  ├── dashboard.html             # Main dashboard
  ├── evidence.html              # Evidence viewer
  ├── devices.html               # Device management
  └── config.html                # Rule configuration
static/                          # Static assets (if using Flask)
  ├── css/
  │   └── style.css              # Custom styles
  ├── js/
  │   └── dashboard.js           # Frontend JavaScript
  └── img/
      └── logo.png               # AutoGuard logo
```

**If migrating to React:**
```
dashboard/                       # React app directory
  ├── src/
  │   ├── components/            # React components
  │   │   ├── LiveFeed.jsx
  │   │   ├── IncidentTimeline.jsx
  │   │   ├── EvidenceViewer.jsx
  │   │   ├── DeviceManager.jsx
  │   │   └── RuleConfig.jsx
  │   ├── App.jsx                # Main app component
  │   └── index.jsx              # Entry point
  ├── public/
  │   └── index.html             # HTML template
  └── package.json               # Dependencies
```

---

## Dependencies on Other Modules

- **Backend API** (`src/server.py`): Dashboard makes REST API calls
- **Evidence Module** (`src/evidence.py`): Dashboard displays evidence files
- **Pairing Service** (planned): Dashboard generates codes and lists devices
- **Live Camera Feed** (planned): Dashboard streams from edge module

---

## Known Issues & TODOs

### Critical (MVP Blockers)
- ❌ **No live camera feed** (static evidence only)
- ❌ **No incident timeline** (no chronological list)
- ❌ **No device management UI** (pairing service not built)
- ❌ **No rule configuration UI** (must edit YAML manually)

### High Priority
- ⚠️ **Very basic UI** (needs professional polish for presentation)
- ⚠️ **No authentication enforcement** (env tokens not checked)
- ⚠️ **Path traversal vulnerability** in `/evidence/image` endpoint
- ⚠️ **No HTTPS/TLS** (plaintext HTTP)

### Medium Priority
- 🔧 **No analytics/metrics** (no incident statistics)
- 🔧 **No evidence export** (can't download ZIP with manifest)
- 🔧 **No search/filter** (no way to find specific incidents)
- 🔧 **No pagination** (all evidence loaded at once)

### Low Priority
- 🔧 **No dark mode** (single theme only)
- 🔧 **Not mobile-responsive** (desktop-only layout)
- 🔧 **No accessibility features** (no ARIA labels, keyboard nav)

---

## Security Considerations

**Current Security Issues:**
- ❌ Path traversal in `/evidence/image?path=` (no sanitization)
- ❌ No CSRF protection
- ❌ No authentication enforcement (tokens optional)
- ❌ No rate limiting
- ❌ No TLS/HTTPS

**Required for MVP (Week 7-8):**
- JWT-based authentication
- Role-based access control (manager vs staff)
- Input validation and sanitization
- HTTPS/TLS for all traffic
- Secure session management

---

## Testing

**Current State:** ❌ No automated tests

**Required Tests (Not Written Yet):**
- [ ] Dashboard loads successfully
- [ ] Evidence list API returns valid JSON
- [ ] Evidence image serving works
- [ ] Pairing code generation (after implementing)
- [ ] Device list displays correctly (after implementing)
- [ ] Rule configuration save/load (after implementing)

---

## Runbook / Operational Notes

### Starting the Dashboard (Current)

```powershell
# Start Flask server
python -m src.server

# Access at http://localhost:5000
# Navigate to http://localhost:5000/dashboard
```

### Troubleshooting

**Dashboard shows no evidence:**
- Check `evidence/` directory has .jpg files
- Check file permissions (read access)
- Check Flask server logs for errors

**Images not loading:**
- Check browser console for 404 errors
- Check evidence file paths (no spaces or special chars)

**Dashboard looks broken:**
- If using CDN for Bootstrap, check internet connection
- Clear browser cache
- Check browser console for CSS/JS errors

---

**Last Updated:** 2026-08-26  
**Next Review:** After implementing live feed and device management (Week 8)  
**Maintainer:** AutoGuard Development Team
