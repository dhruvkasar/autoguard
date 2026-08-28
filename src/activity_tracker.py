"""
Activity tracking for live feed statistics
Tracks real-time activity data across processes
"""
import os
import json
import time
from collections import deque
from datetime import datetime


class ActivityTracker:
    """Tracks live activity data for web dashboard"""
    
    def __init__(self, cache_dir="stream_cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.activity_path = os.path.join(cache_dir, "activity.json")
        self.detections_path = os.path.join(cache_dir, "recent_detections.json")
        self.recent_detections = deque(maxlen=10)
        
    def update_activity(self, tracked_count, zone_counts, fps=0, detection_latency=0):
        """Update current activity stats"""
        max_retries = 3
        retry_delay = 0.01  # 10ms
        
        for attempt in range(max_retries):
            try:
                data = {
                    'timestamp': time.time(),
                    'tracked_objects': tracked_count,
                    'zone_counts': zone_counts,  # {'shelf': 2, 'checkout': 0, 'exit': 1}
                    'fps': fps,
                    'detection_latency': detection_latency
                }
                
                temp_path = self.activity_path + f".tmp{os.getpid()}"
                with open(temp_path, 'w') as f:
                    json.dump(data, f)
                
                try:
                    if os.path.exists(self.activity_path):
                        os.remove(self.activity_path)
                except (PermissionError, OSError):
                    time.sleep(retry_delay)
                    if attempt < max_retries - 1:
                        continue
                
                os.rename(temp_path, self.activity_path)
                break  # Success
                
            except (PermissionError, OSError):
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
            except Exception as e:
                if "WinError 32" not in str(e):
                    print(f"Error updating activity: {e}")
                break
    
    def add_detection_event(self, track_id, zone, event_type="zone_change"):
        """Add a detection event to recent history"""
        max_retries = 3
        retry_delay = 0.01  # 10ms
        
        for attempt in range(max_retries):
            try:
                event = {
                    'track_id': track_id,
                    'zone': zone,
                    'event_type': event_type,
                    'timestamp': time.time(),
                    'time_ago': 'Just now'
                }
                
                self.recent_detections.append(event)
                
                # Save to file
                temp_path = self.detections_path + f".tmp{os.getpid()}"
                with open(temp_path, 'w') as f:
                    json.dump(list(self.recent_detections), f)
                
                try:
                    if os.path.exists(self.detections_path):
                        os.remove(self.detections_path)
                except (PermissionError, OSError):
                    time.sleep(retry_delay)
                    if attempt < max_retries - 1:
                        continue
                
                os.rename(temp_path, self.detections_path)
                break  # Success
                
            except (PermissionError, OSError):
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
            except Exception as e:
                if "WinError 32" not in str(e):
                    print(f"Error adding detection event: {e}")
                break
    
    def get_activity(self):
        """Get current activity data"""
        try:
            if not os.path.exists(self.activity_path):
                return {
                    'tracked_objects': 0,
                    'zone_counts': {'shelf': 0, 'checkout': 0, 'exit': 0},
                    'fps': 0,
                    'detection_latency': 0,
                    'timestamp': 0
                }
            
            with open(self.activity_path, 'r') as f:
                return json.load(f)
                
        except Exception:
            return {
                'tracked_objects': 0,
                'zone_counts': {'shelf': 0, 'checkout': 0, 'exit': 0},
                'fps': 0,
                'detection_latency': 0,
                'timestamp': 0
            }
    
    def get_recent_detections(self):
        """Get recent detection events"""
        try:
            if not os.path.exists(self.detections_path):
                return []
            
            with open(self.detections_path, 'r') as f:
                detections = json.load(f)
            
            # Update time_ago for each detection
            now = time.time()
            for det in detections:
                elapsed = now - det['timestamp']
                if elapsed < 60:
                    det['time_ago'] = f"{int(elapsed)}s ago"
                elif elapsed < 3600:
                    det['time_ago'] = f"{int(elapsed/60)}m ago"
                else:
                    det['time_ago'] = f"{int(elapsed/3600)}h ago"
            
            return detections
            
        except Exception:
            return []


# Global singleton
_activity_tracker = None

def get_activity_tracker():
    """Get the global activity tracker instance"""
    global _activity_tracker
    if _activity_tracker is None:
        _activity_tracker = ActivityTracker()
    return _activity_tracker
