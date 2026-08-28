import os
import argparse
import time
from typing import Optional

import cv2
try:
    import winsound
except Exception:
    winsound = None
import numpy as np
import supervision as sv

from .config_loader import load_config
from .logging_config import setup_logging
from .detector import YOLODetector
from .tracker import ByteTrackerWrapper
from .zones import Zone, ZoneManager, Line, segments_intersect
from .rules import BehaviorEngine
from .utils import box_center, draw_id
from .evidence import save_evidence, prune_old_evidence
from .alerts import TelegramAlerter
from .description_generator import get_generator
from .stream_manager import get_stream_manager
from .activity_tracker import get_activity_tracker


def build_zones(cfg) -> ZoneManager:
    colors = {
        "shelf": (255, 255, 0),
        "checkout": (255, 0, 255),
        "exit": (0, 255, 255),
    }
    zones = []
    for name in ["shelf", "checkout", "exit"]:
        rect = cfg["zones"][name]
        zones.append(Zone(name=name, rect=tuple(rect), color=colors.get(name, (0, 255, 255))))
    return ZoneManager(zones)


def process_stream(source: str, cfg):
    logger = setup_logging(cfg["storage"]["logs_dir"]) if "storage" in cfg else setup_logging("logs")
    logger.info("System start")

    # Components
    det = YOLODetector(weights=cfg["model"]["weights"], confidence_threshold=cfg["model"]["confidence_threshold"], device=cfg["model"].get("device", "auto"))
    trk = ByteTrackerWrapper(track_threshold=cfg["tracking"]["track_threshold"], match_threshold=cfg["tracking"]["match_threshold"])
    zones = build_zones(cfg)
    engine = BehaviorEngine(
        loitering_seconds=cfg["rules"]["loitering_seconds"],
        shelf_exit_repeat_count=cfg["rules"]["shelf_exit_repeat_count"],
        shelf_exit_time_window_seconds=cfg["rules"]["shelf_exit_time_window_seconds"],
    )
    alerter = TelegramAlerter(
        enabled=cfg["alerts"].get("enabled", True),
        token=cfg["alerts"].get("token"),
        chat_ids=cfg["alerts"].get("chat_ids", []),
        camera_id=cfg["alerts"].get("camera_id", "CAM01"),
        logger=logger,
    )
    
    # AI Description Generator
    desc_gen = get_generator()

    evidence_dir = cfg["storage"]["evidence_dir"]
    os.makedirs(evidence_dir, exist_ok=True)
    # Prune old evidence based on retention policy
    retention_days = int(cfg.get("storage", {}).get("retention_days", 0))
    if retention_days > 0:
        prune_old_evidence(evidence_dir, retention_days, logger)

    # Optional checkout line for crossing detection
    checkout_line = None
    if cfg.get("lines", {}).get("checkout"):
        cx1, cy1, cx2, cy2 = cfg["lines"]["checkout"]
        checkout_line = Line((int(cx1), int(cy1)), (int(cx2), int(cy2)))

    # Video capture with detailed diagnostics
    camera_index = int(source) if str(source).isdigit() else source
    logger.info(f"Attempting to open camera source: {camera_index}")
    
    # Function to test if camera has actual video data
    def test_camera_has_video(cap_obj):
        ret, frame = cap_obj.read()
        if not ret or frame is None:
            return False, None
        # Check if frame has actual video data (not all zeros/ones)
        if frame.max() <= 1:  # Dummy camera with no real data
            logger.warning(f"Camera has no real video data (max pixel value: {frame.max()})")
            return False, None
        return True, frame
    
    cap = cv2.VideoCapture(camera_index)
    working_camera = False
    test_frame = None
    
    if cap.isOpened():
        has_video, test_frame = test_camera_has_video(cap)
        if has_video:
            working_camera = True
            logger.info(f"Camera {camera_index} opened successfully with real video data")
        else:
            logger.warning(f"Camera {camera_index} opened but has no real video data")
            cap.release()
    else:
        logger.error(f"Failed to open camera source: {camera_index}")
    
    # If initial camera doesn't work, try alternatives
    if not working_camera:
        logger.info("Trying alternative camera indices...")
        for alt_index in [1, 0, 2]:
            if alt_index == camera_index:
                continue
            logger.info(f"Trying camera index {alt_index}...")
            cap = cv2.VideoCapture(alt_index)
            if cap.isOpened():
                has_video, test_frame = test_camera_has_video(cap)
                if has_video:
                    logger.info(f"Successfully opened camera at index {alt_index} with real video")
                    camera_index = alt_index
                    working_camera = True
                    break
                else:
                    logger.warning(f"Camera {alt_index} has no real video data, skipping")
                    cap.release()
        
        if not working_camera:
            logger.error("Could not find any working camera with real video. Please check:")
            logger.error("1. Camera is connected and not in use by another application")
            logger.error("2. Camera permissions are granted")
            logger.error("3. Camera drivers are installed")
            logger.error("4. Close any other apps using the camera (Zoom, Teams, etc.)")
            raise RuntimeError("Failed to initialize camera with real video")
    
    logger.info(f"Camera opened successfully: {camera_index}")
    
    # Set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, cfg["video"]["width"])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cfg["video"]["height"])
    
    logger.info(f"Camera initialized: {test_frame.shape[1]}x{test_frame.shape[0]}, pixel range: {test_frame.min()}-{test_frame.max()}")

    display = bool(cfg["video"].get("display", True))
    dbg = cfg.get("debug", {})
    dbg_overlay = bool(dbg.get("overlay", True))
    dbg_verbose = bool(dbg.get("verbose", True))
    # Allow disabling checkout line logic and rely only on checkout zone
    use_checkout_line = bool(cfg.get("rules", {}).get("use_checkout_line", True))
    audio = cfg.get("audio", {})
    beep_enabled = bool(audio.get("beep_enabled", True)) and winsound is not None
    beep_exit = bool(audio.get("exit_beep", True))
    beep_loiter = bool(audio.get("loiter_beep", True))
    beep_freq = int(audio.get("beep_frequency", 1000))
    beep_ms = int(audio.get("beep_duration_ms", 300))
    beep_cd = int(audio.get("beep_cooldown_seconds", 5))

    # Track previous centers per ID for line-crossing detection
    prev_centers = {}

    # Alert hygiene state
    last_alert_times = {}
    daily_counts = {"date": time.strftime("%Y-%m-%d"), "count": 0}
    cooldown = int(cfg["alerts"].get("cooldown_seconds", 0))
    daily_cap = int(cfg["alerts"].get("daily_cap", 0))
    # Beep cooldown state
    last_beep_times = {}
    
    # Stream manager for web dashboard
    stream_mgr = get_stream_manager()
    activity_tracker = get_activity_tracker()
    logger.info("Stream manager initialized for web dashboard")

    frame_count = 0
    fps_start_time = time.time()
    fps_frame_count = 0
    current_fps = 0
    detection_start = 0
    detection_latency = 0
    last_zone_state = {}  # Track zone changes for detection events
    try:
        while True:
            ok, frame = cap.read()
            if not ok or frame is None:
                logger.error(f"Failed to read frame from source at frame {frame_count}.")
                logger.info("Attempting to reconnect to camera...")
                cap.release()
                time.sleep(1)
                cap = cv2.VideoCapture(camera_index)
                if not cap.isOpened():
                    logger.error("Could not reconnect to camera. Exiting.")
                    break
                continue
            
            frame_count += 1

            # Calculate FPS
            fps_frame_count += 1
            if time.time() - fps_start_time >= 1.0:
                current_fps = fps_frame_count / (time.time() - fps_start_time)
                fps_frame_count = 0
                fps_start_time = time.time()

            # Add status overlay to show camera is working
            if display:
                # Draw camera status
                status_text = f"CAM: {cfg['alerts'].get('camera_id', 'CAM01')} | Frame: {frame_count} | LIVE"
                cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                # Draw timestamp
                timestamp_text = time.strftime("%Y-%m-%d %H:%M:%S")
                cv2.putText(frame, timestamp_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

            # Detection with timing
            detection_start = time.time()
            detections = det.detect(frame)
            detection_latency = (time.time() - detection_start) * 1000  # Convert to ms
            if detections is None or len(detections) == 0:
                # Update activity with zero counts
                activity_tracker.update_activity(
                    tracked_count=0,
                    zone_counts={'shelf': 0, 'checkout': 0, 'exit': 0},
                    fps=current_fps,
                    detection_latency=detection_latency
                )
                
                # Update stream manager
                stream_mgr.update_frame(frame)
                
                if display:
                    zones.draw_all(frame)
                    # Draw "No detections" indicator
                    cv2.putText(frame, "No persons detected", (10, frame.shape[0] - 20), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 2)
                    cv2.imshow("AutoGuard", frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                continue

            # Tracking
            tracked = trk.update(detections)

            # Draw zones
            if display:
                zones.draw_all(frame)
                if checkout_line is not None:
                    checkout_line.draw(frame)
            
            # Count people in each zone
            zone_counts = {'shelf': 0, 'checkout': 0, 'exit': 0}

            # Per tracked object
            for i, xyxy in enumerate(tracked.xyxy):
                # track IDs are in tracker_id
                track_id = int(tracked.tracker_id[i]) if tracked.tracker_id is not None else -1
                center = box_center(xyxy)
                zone = zones.locate(center)
                
                # Count zone occupancy
                if zone and zone in zone_counts:
                    zone_counts[zone] += 1
                
                # Track zone changes for activity feed
                prev_zone = last_zone_state.get(track_id)
                if zone and zone != prev_zone:
                    activity_tracker.add_detection_event(track_id, zone, "zone_change")
                    last_zone_state[track_id] = zone
                
                crossed_checkout = False
                if use_checkout_line and checkout_line is not None:
                    prev = prev_centers.get(track_id)
                    if prev is not None and segments_intersect(prev, center, checkout_line.p1, checkout_line.p2):
                        crossed_checkout = True
                        if dbg_verbose:
                            logger.info(f"ID {track_id} crossed checkout line")
                now_ts = time.time()
                triggers = engine.update(track_id, zone, now=now_ts, crossed_checkout=crossed_checkout)
                prev_centers[track_id] = center

                # Draw box and ID
                # Choose color dynamically
                color = (0, 255, 0)
                st = engine.persons.get(track_id)
                if st:
                    if zone == "shelf" and st.shelf_enter_time:
                        elapsed = now_ts - st.shelf_enter_time
                        if elapsed >= engine.loitering_seconds:
                            color = (0, 0, 255)  # red when loiter threshold reached
                        elif elapsed > 0:
                            color = (0, 165, 255)  # orange while accumulating
                    elif zone == "exit" and st.visited_shelf and not st.visited_checkout:
                        color = (0, 0, 255)  # red when exiting without checkout state
                draw_id(frame, xyxy, track_id, color)

                # Overlay zone and checkout status
                if display and dbg_overlay:
                    x1, y1, x2, y2 = map(int, xyxy)
                    ck = engine.persons.get(track_id).visited_checkout if track_id in engine.persons else False
                    ztxt = zone if zone else "none"
                    cv2.putText(frame, f"zone:{ztxt} ck:{'Y' if ck else 'N'}", (x1, y2 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

                for rule in triggers:
                    # Beep alarm on key rules with cooldown
                    if beep_enabled:
                        if (rule.startswith("Exit Without Checkout") and beep_exit) or (rule.startswith("Loitering") and beep_loiter):
                            bkey = (rule, track_id)
                            if (now_ts - last_beep_times.get(bkey, 0)) >= beep_cd:
                                try:
                                    winsound.Beep(beep_freq, beep_ms)
                                except Exception:
                                    pass
                                last_beep_times[bkey] = now_ts
                    
                    # Generate AI description
                    st = engine.persons.get(track_id)
                    dwell_time = 0
                    if st and st.shelf_enter_time:
                        dwell_time = now_ts - st.shelf_enter_time
                    
                    context = {
                        'person_id': track_id,
                        'zone': zone,
                        'dwell_time': dwell_time,
                        'camera_id': cfg["alerts"].get("camera_id", "CAM01"),
                        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
                        'visited_shelf': st.visited_shelf if st else False,
                        'visited_checkout': st.visited_checkout if st else False,
                        'repeat_count': cfg["rules"]["shelf_exit_repeat_count"],
                        'time_window': cfg["rules"]["shelf_exit_time_window_seconds"],
                    }
                    
                    description = desc_gen.generate(rule, context)
                    priority = desc_gen.get_priority(rule)
                    
                    # Save evidence with AI description
                    path = save_evidence(frame.copy(), xyxy, track_id, rule, evidence_dir, 
                                       cfg["alerts"].get("camera_id", "CAM01"), logger, 
                                       description=description, priority=priority)
                    
                    # Send alert with cooldown and daily cap
                    key = (rule, track_id)
                    today = time.strftime("%Y-%m-%d")
                    if daily_counts["date"] != today:
                        daily_counts["date"], daily_counts["count"] = today, 0

                    allowed_by_cooldown = True
                    if cooldown > 0 and (now_ts - last_alert_times.get(key, 0)) < cooldown:
                        allowed_by_cooldown = False

                    allowed_by_cap = True
                    if daily_cap > 0 and daily_counts["count"] >= daily_cap:
                        allowed_by_cap = False

                    if allowed_by_cooldown and allowed_by_cap:
                        # Use AI description in alert caption
                        caption = f"🚨 {rule}\n\n{description}\n\nCamera: {cfg['alerts'].get('camera_id', 'CAM01')}\nTime: {time.strftime('%Y-%m-%d %H:%M:%S')}"
                        alerter.send_photo(path, caption)
                        last_alert_times[key] = now_ts
                        daily_counts["count"] += 1
                        logger.info(f"Alert requested for rule='{rule}' id={track_id} | Description: {description[:80]}...")
                    else:
                        reason = []
                        if not allowed_by_cooldown:
                            reason.append("cooldown")
                        if not allowed_by_cap:
                            reason.append("daily-cap")
                        logger.info(f"Alert suppressed ({'+'.join(reason)}) for rule='{rule}' id={track_id}")
            
            # Update activity tracker with current stats
            tracked_count = len(tracked.xyxy) if tracked.xyxy is not None else 0
            activity_tracker.update_activity(
                tracked_count=tracked_count,
                zone_counts=zone_counts,
                fps=current_fps,
                detection_latency=detection_latency
            )

            # Update stream manager for web dashboard (send a copy with all overlays)
            stream_mgr.update_frame(frame)
            
            if display:
                cv2.imshow("AutoGuard", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
    finally:
        cap.release()
        if display:
            cv2.destroyAllWindows()
        logger.info("System stop")


def parse_args():
    ap = argparse.ArgumentParser(description="AutoGuard MVP")
    ap.add_argument("--source", type=str, default=None, help="Video source: 0 for webcam or path to file")
    return ap.parse_args()


if __name__ == "__main__":
    cfg = load_config()
    args = parse_args()
    src = args.source if args.source is not None else str(cfg["video"]["source"]) if isinstance(cfg["video"]["source"], int) else cfg["video"]["source"]
    process_stream(str(src), cfg)
