# Edge Module – Video Pipeline, Detection, Tracking & Behavior Analysis

**Module:** Edge Layer (Camera → Detection → Tracking → Rules)  
**Status:** ✅ Core theft detection working, ⚠️ Violence detection not started  
**Last Updated:** 2026-08-26  
**Owner:** Cybersecurity Final Year Project Team

---

## Purpose

The Edge module handles the entire video processing pipeline from camera input through person detection, multi-object tracking, zone-based behavior analysis, and rule triggering. This is the "eyes and brain" of AutoGuard that runs continuously on the store PC or edge device.

**Key Responsibilities:**
- Capture live video from cameras (webcam, IP camera, RTSP)
- Detect persons in each frame using YOLOv8
- Track individuals across frames with ByteTrack
- Maintain per-person state (zone history, timers, flags)
- Evaluate theft-indicative and violence-indicative behavior rules
- Trigger evidence capture and alerts when rules fire

---

## Architecture

```
Camera Feed (OpenCV)
  ↓
YOLODetector (YOLOv8n)
  ↓
ByteTrackerWrapper (supervision library)
  ↓
ZoneManager (locate person in zones)
  ↓
BehaviorEngine (rule evaluation per track ID)
  ↓
Evidence Capture + Alert Dispatch
```

---

## Public Interfaces

### Entry Point

**File:** `src/main.py`

**Function:** `process_stream(source: str, cfg: dict) -> None`
- Main video processing loop
- **Parameters:**
  - `source`: Camera source ("0" for webcam, path for video file, RTSP URL)
  - `cfg`: Configuration dict loaded from `config/config.yaml`
- **Returns:** None (runs until interrupted or video ends)
- **Side Effects:** Writes evidence to disk, sends alerts, displays video window

**CLI Usage:**
```bash
python src/main.py --source 0           # Webcam
python src/main.py --source video.mp4   # File
python src/main.py --source rtsp://...  # IP camera
```

---

### Detection

**File:** `src/detector.py`

**Class:** `YOLODetector`
- Wraps Ultralytics YOLOv8 for person detection
- **Constructor:** `__init__(weights: str, confidence_threshold: float, device: str = "auto")`
  - `weights`: Path to YOLOv8 weights (e.g., "yolov8n.pt")
  - `confidence_threshold`: Min confidence for detection (0.0-1.0)
  - `device`: "cpu", "cuda", or "auto"
- **Method:** `detect(frame: np.ndarray) -> sv.Detections`
  - **Parameters:** OpenCV frame (BGR numpy array)
  - **Returns:** supervision Detections object with xyxy boxes, confidences, class IDs
  - Filters to person class (COCO class 0) only

**Dependencies:** ultralytics, supervision, numpy

---

### Tracking

**File:** `src/tracker.py`

**Class:** `ByteTrackerWrapper`
- Wraps ByteTrack via supervision library for multi-object tracking
- **Constructor:** `__init__(track_threshold: float, match_threshold: float)`
  - `track_threshold`: Min confidence to start tracking (default 0.3)
  - `match_threshold`: IoU threshold for matching detections to tracks (default 0.8)
- **Method:** `update(detections: sv.Detections) -> sv.Detections`
  - **Parameters:** Detection results from current frame
  - **Returns:** Detections with `tracker_id` field added (unique per tracked person)
  - Track IDs are session-scoped integers; reused after track lost

**Dependencies:** supervision (includes ByteTrack implementation)

**Technical Notes:**
- ByteTrack chosen over DeepSORT (better performance, simpler)
- Track IDs reset when person leaves frame for extended period
- No appearance features used (purely motion-based matching)

---

### Zone Management

**File:** `src/zones.py`

**Class:** `Zone`
- Represents a rectangular region in the camera view
- **Constructor:** `__init__(name: str, rect: tuple[int, int, int, int], color: tuple[int, int, int])`
  - `name`: Zone identifier ("shelf", "checkout", "exit")
  - `rect`: (x1, y1, x2, y2) pixel coordinates
  - `color`: BGR color tuple for visualization
- **Method:** `contains(point: tuple[int, int]) -> bool`
  - **Parameters:** (cx, cy) center point
  - **Returns:** True if point inside rectangle

**Class:** `ZoneManager`
- Manages multiple zones
- **Constructor:** `__init__(zones: list[Zone])`
- **Method:** `locate(point: tuple[int, int]) -> Optional[str]`
  - **Parameters:** (cx, cy) center point of bounding box
  - **Returns:** Zone name or None if not in any zone
- **Method:** `draw_all(frame: np.ndarray) -> None`
  - Draws all zone rectangles on frame (mutates in-place)

**Class:** `Line`
- Represents a line segment for crossing detection (optional)
- **Constructor:** `__init__(p1: tuple[int, int], p2: tuple[int, int])`
- **Method:** `draw(frame: np.ndarray) -> None`

**Function:** `segments_intersect(p1, p2, p3, p4) -> bool`
- Line segment intersection test (for checkout line crossing)

**Interactive Tool:** `src/zone_calibrator.py`
- GUI tool for drawing zone rectangles on camera snapshot
- Outputs coordinates to copy into `config/config.yaml`
- Usage: `python -m src.zone_calibrator`

---

### Behavior Analysis & Rule Engine

**File:** `src/rules.py`

**Class:** `PersonState`
- Dataclass tracking state for one tracked person
- **Fields:**
  - `last_zone: Optional[str]` - Current zone ("shelf", "checkout", "exit", or None)
  - `shelf_enter_time: Optional[float]` - Timestamp when entered shelf zone
  - `visited_checkout: bool` - Flag if person passed through checkout
  - `visited_shelf: bool` - Flag if person visited shelf at any point
  - `transitions: List[str]` - Sequence of zones visited

**Class:** `BehaviorEngine`
- State machine managing rules for all tracked persons
- **Constructor:** `__init__(loitering_seconds: int, shelf_exit_repeat_count: int, shelf_exit_time_window_seconds: int)`
  - `loitering_seconds`: Threshold for Loitering rule
  - `shelf_exit_repeat_count`: Min occurrences for Repeated Shelf-Exit rule
  - `shelf_exit_time_window_seconds`: Time window for pattern detection
- **Method:** `update(person_id: int, zone: Optional[str], now: float = None, crossed_checkout: bool = False) -> List[str]`
  - **Parameters:**
    - `person_id`: Track ID from ByteTrack
    - `zone`: Current zone name or None
    - `now`: Timestamp (defaults to time.time())
    - `crossed_checkout`: True if person crossed optional checkout line
  - **Returns:** List of triggered rule names (empty if no triggers)
  - **Side Effects:** Updates internal `self.persons` state dict

**Implemented Rules:**

1. **Loitering in Shelf Zone**
   - Trigger: Person remains in shelf zone ≥ `loitering_seconds`
   - Behavior: Timer starts on shelf entry, resets on zone exit
   - Config: `rules.loitering_seconds` (default: 5 for demo, 30+ for production)

2. **Repeated Shelf-Exit Movement**
   - Trigger: Person moves between shelf and exit ≥ `repeat_count` times within `time_window`
   - Behavior: Counts zone transitions within sliding window
   - Config: `rules.shelf_exit_repeat_count` (default: 2), `rules.shelf_exit_time_window_seconds` (default: 60)

3. **Exit Without Checkout**
   - Trigger: Person visited shelf, then moved to exit, without visiting checkout zone
   - Behavior: State flags tracked per person
   - Alternative: Optional checkout line crossing (config: `rules.use_checkout_line`)

**Not Yet Implemented (Week 4-5 Planned):**

4. **Aggressive Pose Detection** (Violence)
   - Trigger: Raised arms, shoving posture, rapid close approach
   - Requires: Pose estimation (MediaPipe or OpenPose)

5. **Rapid Clustering/Dispersal** (Violence)
   - Trigger: Sudden multi-person movement (crowd fleeing/converging)
   - Requires: Track velocity vectors across multiple IDs

6. **Elevated Object Detection** (Violence)
   - Trigger: Long/rigid handheld object in raised posture
   - Flagged as "elevated object for review" NOT "weapon confirmed"

7. **Group Freeze Posture** (Violence)
   - Trigger: Multiple people static simultaneously (hold-up signature)
   - Requires: Velocity tracking across multiple IDs

---

### Utilities

**File:** `src/utils.py`

**Function:** `box_center(xyxy: np.ndarray) -> tuple[int, int]`
- **Parameters:** Bounding box [x1, y1, x2, y2]
- **Returns:** (cx, cy) center point

**Function:** `draw_id(frame: np.ndarray, xyxy: np.ndarray, track_id: int, color: tuple) -> None`
- Draws bounding box + track ID label on frame (mutates in-place)
- Color encodes state (green=normal, orange=accumulating loiter, red=rule triggered)

---

## Key File Paths

```
src/main.py              # Entry point, video loop
src/detector.py          # YOLOv8 wrapper
src/tracker.py           # ByteTrack wrapper
src/zones.py             # Zone and ZoneManager classes
src/rules.py             # BehaviorEngine and PersonState
src/utils.py             # Helper functions
src/zone_calibrator.py   # Interactive zone drawing tool
config/config.yaml       # Zone coordinates, thresholds
yolov8n.pt               # YOLOv8 nano weights (downloaded)
```

---

## Configuration

**File:** `config/config.yaml`

```yaml
model:
  weights: yolov8n.pt
  confidence_threshold: 0.35
  device: auto  # "cpu", "cuda", or "auto"

tracking:
  track_threshold: 0.3
  match_threshold: 0.8

zones:
  shelf: [x1, y1, x2, y2]    # Pixel coordinates
  checkout: [x1, y1, x2, y2]
  exit: [x1, y1, x2, y2]

rules:
  loitering_seconds: 5             # DEMO VALUE (use 30+ production)
  shelf_exit_repeat_count: 2
  shelf_exit_time_window_seconds: 60
  use_checkout_line: false         # Set true to enable line crossing

lines:  # Optional checkout line for crossing detection
  checkout: [x1, y1, x2, y2]       # Empty dict if not used

video:
  source: 0          # 0=webcam, path for file, rtsp:// for IP cam
  width: 1280
  height: 720
  display: true      # Show OpenCV window

debug:
  overlay: true      # Show zone labels on boxes
  verbose: true      # Log zone transitions

audio:
  beep_enabled: true        # Local audio alerts (Windows only)
  beep_frequency: 1000
  beep_duration_ms: 300
  beep_cooldown_seconds: 5
  exit_beep: true           # Beep on Exit Without Checkout
  loiter_beep: true         # Beep on Loitering
```

---

## Dependencies on Other Modules

- **Evidence Module** (`src/evidence.py`): Called to save snapshots when rules trigger
- **Alerts Module** (`src/alerts.py`): Called to dispatch Telegram alerts
- **Config Loader** (`src/config_loader.py`): Loads YAML config at startup
- **Logging** (`src/logging_config.py`): Structured logging for audit trail

---

## Known Issues & TODOs

### High Priority
- ❌ **Violence detection rules not implemented** (Week 4-5 planned)
  - Requires pose estimation library integration (MediaPipe recommended)
  - Requires ethical test footage sourcing
- ⚠️ **Demo thresholds too low** (5s loiter causes false positives)
  - Acceptable for demo, but needs tuning for production
  - Recommend 30-60s loitering threshold in real deployment

### Medium Priority
- ⚠️ **Track ID reuse** after person leaves frame (expected ByteTrack behavior)
  - Could cause false positives if same ID assigned to different person
  - Mitigation: Add appearance-based re-identification (post-MVP)
- ⚠️ **Single camera only** (architecture supports multi-cam but not tested)
  - Each camera needs separate capture+detection+tracking worker
  - Future: Correlate tracks across cameras
- ⚠️ **No graceful shutdown** (Ctrl+C works but no cleanup)
  - Add signal handler to release camera and log shutdown

### Low Priority
- 🔧 **Checkout line crossing optional** (zone-based detection sufficient for MVP)
  - Line intersection logic exists but disabled by default
- 🔧 **Hard-coded person class filter** (COCO class 0)
  - Sufficient for retail use case
- 🔧 **No confidence score logging** (only binary detection)
  - Could be useful for tuning thresholds

---

## Testing

**File:** `tests/test_rules.py`

**Covered:**
- ✅ Loitering rule trigger after threshold
- ✅ Loitering rule non-trigger before threshold
- ✅ Exit Without Checkout trigger
- ✅ Exit Without Checkout non-trigger (visited checkout)
- ✅ Repeated Shelf-Exit pattern detection

**Not Covered:**
- ❌ Detector accuracy tests
- ❌ Tracker consistency tests (same person across frames)
- ❌ Zone boundary edge cases
- ❌ Multi-person scenarios (concurrent tracks)
- ❌ Violence detection rules (not implemented yet)

**Test Approach:**
- Unit tests use synthetic state updates (no video required)
- Integration tests planned with recorded sample clips

---

## Performance Characteristics

**Hardware Requirements:**
- CPU: Quad-core 2.0+ GHz (YOLOv8n is lightweight)
- RAM: 4GB minimum (8GB recommended)
- GPU: Optional (CUDA-capable for faster inference)
- Camera: 1280x720 minimum resolution

**Measured Performance (on reference system):**
- Frame rate: 15-25 FPS (CPU), 30+ FPS (GPU)
- Detection latency: 40-60ms per frame (YOLOv8n)
- End-to-end alert latency: 1-2 seconds (detection to evidence saved)

**Bottlenecks:**
- YOLOv8 inference (largest component)
- Mitigations: Use GPU, reduce frame size, skip frames (process every Nth frame)

---

## Security Considerations

**Privacy by Design:**
- ✅ No facial recognition (anonymous track IDs only)
- ✅ Track IDs are session-scoped (reset on restart)
- ✅ No persistent identity across sessions
- ✅ No biometric feature extraction

**Data Handling:**
- ⚠️ Raw frames held in memory only (not logged)
- ⚠️ Snapshots saved to disk on rule trigger (not yet encrypted)
- ✅ No frames sent to external APIs (all processing local)

**Threat Model:**
- 🔒 Physical access to edge device → can view live feed (expected)
- 🔒 Physical access to evidence dir → can view snapshots (encryption planned Week 7)
- 🔒 Network sniffing → frames never leave device (no risk)

---

## Future Enhancements (Post-MVP)

1. **Multi-camera support** with track correlation across views
2. **Violence detection** (pose + object detection)
3. **Appearance-based re-identification** to reduce track ID reuse issues
4. **Adaptive threshold tuning** based on false positive feedback
5. **Object detection integration** (shopping bag, cart) for context
6. **Spatial heatmaps** (dwell time by location, not just zone)
7. **Temporal filtering** (ignore very short zone visits)
8. **Edge GPU optimization** (TensorRT, ONNX Runtime)

---

## Runbook / Operational Notes

### Starting the System

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run with webcam
python src/main.py --source 0

# Run with video file (for testing)
python src/main.py --source test_footage.mp4

# Run with IP camera
python src/main.py --source rtsp://username:password@192.168.1.100/stream
```

### Calibrating Zones

```powershell
# 1. Start zone calibrator (opens camera)
python -m src.zone_calibrator

# 2. Draw rectangles: Click and drag for each zone
#    - Shelf zone (where products are)
#    - Checkout zone (POS/counter area)
#    - Exit zone (doorway)

# 3. Copy printed coordinates into config/config.yaml under "zones:"
```

### Adjusting Thresholds

Edit `config/config.yaml`:
- **Too many loitering alerts?** Increase `rules.loitering_seconds` (try 15-30)
- **Missing exit-without-checkout?** Check zone placement (checkout zone coverage)
- **False shelf-exit alerts?** Increase `rules.shelf_exit_repeat_count` or reduce `time_window`

### Troubleshooting

**No detections / empty frames:**
- Check camera source is correct (webcam index, file path, RTSP URL)
- Check lighting (YOLOv8 needs reasonable visibility)
- Lower `model.confidence_threshold` (try 0.25)

**Tracker IDs jumping:**
- Normal behavior when person leaves frame and returns
- Increase `tracking.match_threshold` for stricter matching (but may fragment tracks)

**High CPU usage:**
- Switch to GPU: `model.device: cuda`
- Reduce frame size: `video.width: 640, video.height: 480`
- Process every Nth frame (code modification needed)

**False positives:**
- Increase rule thresholds (especially loitering_seconds)
- Refine zone placement (exclude doorways from shelf zone)
- Enable alert cooldown (already in config, increase if needed)

---

**Last Updated:** 2026-08-26  
**Next Review:** After implementing violence detection (Week 4-5)  
**Maintainer:** AutoGuard Development Team
