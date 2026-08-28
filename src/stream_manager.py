"""
Shared frame buffer for streaming video to the web dashboard
Uses file-based communication for inter-process sharing with retry logic
"""
import os
import threading
import time
import cv2
import numpy as np
import json


class StreamManager:
    """Manages video frames for streaming to web clients using file-based IPC"""
    
    def __init__(self, stream_dir="stream_cache"):
        self.stream_dir = stream_dir
        os.makedirs(self.stream_dir, exist_ok=True)
        self.frame_path = os.path.join(self.stream_dir, "latest_frame.jpg")
        self.meta_path = os.path.join(self.stream_dir, "frame_meta.json")
        self.lock = threading.Lock()
        self.clients = 0
        self.cached_frame = None
        self.cached_time = 0
        
    def update_frame(self, frame: np.ndarray):
        """Update the current frame (called by detection system)"""
        max_retries = 3
        retry_delay = 0.01  # 10ms
        
        for attempt in range(max_retries):
            try:
                # Encode frame as JPEG
                ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                if not ret:
                    return
                
                # Write frame to temp file then rename (atomic operation)
                temp_path = self.frame_path + f".tmp{os.getpid()}"
                with open(temp_path, 'wb') as f:
                    f.write(buffer.tobytes())
                
                # Rename is atomic - use unique temp file per process
                try:
                    if os.path.exists(self.frame_path):
                        os.remove(self.frame_path)
                except (PermissionError, OSError):
                    time.sleep(retry_delay)
                    if attempt < max_retries - 1:
                        continue
                
                os.rename(temp_path, self.frame_path)
                
                # Update metadata
                meta = {
                    'timestamp': time.time(),
                    'shape': frame.shape
                }
                temp_meta = self.meta_path + f".tmp{os.getpid()}"
                with open(temp_meta, 'w') as f:
                    json.dump(meta, f)
                
                try:
                    if os.path.exists(self.meta_path):
                        os.remove(self.meta_path)
                except (PermissionError, OSError):
                    time.sleep(retry_delay)
                    if attempt < max_retries - 1:
                        continue
                
                os.rename(temp_meta, self.meta_path)
                break  # Success
                
            except (PermissionError, OSError) as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                # Only print error on final failure
                # Suppress frequent errors to avoid spam
            except Exception as e:
                # Only log unexpected errors
                if "WinError 32" not in str(e):
                    print(f"Error updating frame: {e}")
                break
    
    def get_frame(self):
        """Get the latest frame (called by web server)"""
        # Use cached frame if recent (within 100ms)
        now = time.time()
        if self.cached_frame is not None and (now - self.cached_time) < 0.1:
            return self.cached_frame
        
        try:
            if not os.path.exists(self.frame_path):
                # No frame available yet
                blank = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(blank, "Waiting for video feed...", (120, 240),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                cv2.putText(blank, "Make sure detection system is running", (80, 280),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
                return blank
            
            # Read frame from file
            frame = cv2.imread(self.frame_path)
            if frame is None:
                blank = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(blank, "Error reading video feed", (120, 240),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                return blank
            
            # Cache the frame
            self.cached_frame = frame
            self.cached_time = now
            
            return frame
            
        except Exception as e:
            print(f"Error reading frame: {e}")
            blank = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(blank, f"Error: {str(e)}", (100, 240),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            return blank
    
    def get_jpeg_frame(self):
        """Get the latest frame as JPEG bytes"""
        # If we have the JPEG file, read it directly for efficiency
        try:
            if os.path.exists(self.frame_path):
                with open(self.frame_path, 'rb') as f:
                    return f.read()
        except Exception:
            pass
        
        # Fallback: encode from frame
        frame = self.get_frame()
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if not ret:
            return None
        return buffer.tobytes()
    
    def is_active(self):
        """Check if feed is active (updated recently)"""
        try:
            if not os.path.exists(self.meta_path):
                return False
            
            with open(self.meta_path, 'r') as f:
                meta = json.load(f)
            
            last_update = meta.get('timestamp', 0)
            return (time.time() - last_update) < 5.0
            
        except Exception:
            return False
    
    def add_client(self):
        """Track when a client connects"""
        self.clients += 1
    
    def remove_client(self):
        """Track when a client disconnects"""
        self.clients = max(0, self.clients - 1)
    
    def get_stats(self):
        """Get streaming statistics"""
        try:
            last_update = 0
            if os.path.exists(self.meta_path):
                with open(self.meta_path, 'r') as f:
                    meta = json.load(f)
                    last_update = meta.get('timestamp', 0)
            
            return {
                'active': self.is_active(),
                'clients': self.clients,
                'last_update': last_update,
                'has_frame': os.path.exists(self.frame_path)
            }
        except Exception:
            return {
                'active': False,
                'clients': self.clients,
                'last_update': 0,
                'has_frame': False
            }


# Global singleton instance
_stream_manager = None

def get_stream_manager():
    """Get the global stream manager instance"""
    global _stream_manager
    if _stream_manager is None:
        _stream_manager = StreamManager()
    return _stream_manager
