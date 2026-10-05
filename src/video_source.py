"""
Video source module for AutoGuard
Supports multiple video sources: USB cameras, RTSP streams, video files
"""

import cv2
import logging
import time
import os
from typing import Optional, Tuple
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class VideoSource:
    """Abstract video source with reconnection support"""
    
    def __init__(self, source: str, reconnect_delay: int = 5, max_reconnect_attempts: int = 10):
        """
        Initialize video source
        
        Args:
            source: Video source (camera index, RTSP URL, or file path)
            reconnect_delay: Seconds to wait before reconnection attempt
            max_reconnect_attempts: Maximum reconnection attempts before giving up
        """
        self.source = source
        self.reconnect_delay = reconnect_delay
        self.max_reconnect_attempts = max_reconnect_attempts
        self.reconnect_attempts = 0
        self.cap = None
        self.source_type = self._detect_source_type(source)
        self.is_connected = False
        self.last_frame_time = time.time()
        self.frame_timeout = 30  # seconds
        
        logger.info(f"Video source initialized: {self.source_type} - {source}")
    
    def _detect_source_type(self, source: str) -> str:
        """Detect the type of video source"""
        # Check if it's a number (USB camera index)
        if isinstance(source, int) or (isinstance(source, str) and source.isdigit()):
            return "USB"
        
        # Check if it's an RTSP/RTMP URL
        if isinstance(source, str):
            lower_source = source.lower()
            if lower_source.startswith('rtsp://'):
                return "RTSP"
            elif lower_source.startswith('rtmp://'):
                return "RTMP"
            elif lower_source.startswith('http://') or lower_source.startswith('https://'):
                return "HTTP"
            elif os.path.isfile(source):
                return "FILE"
        
        # Default to USB
        return "USB"
    
    def connect(self, width: int = 1280, height: int = 720, buffer_size: int = 1) -> bool:
        """
        Connect to video source
        
        Args:
            width: Desired frame width
            height: Desired frame height
            buffer_size: OpenCV buffer size (1 = minimal latency)
        
        Returns:
            True if connection successful
        """
        try:
            # Convert source to appropriate format
            if self.source_type == "USB":
                source_param = int(self.source) if str(self.source).isdigit() else 0
            else:
                source_param = self.source
            
            # Create VideoCapture with appropriate backend
            if self.source_type == "RTSP":
                # Use FFMPEG backend for RTSP streams (better performance)
                logger.info(f"Connecting to RTSP stream: {source_param}")
                self.cap = cv2.VideoCapture(source_param, cv2.CAP_FFMPEG)
                
                # Set RTSP-specific options for lower latency
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, buffer_size)
                # Enable RTSP over TCP (more reliable than UDP)
                os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'rtsp_transport;tcp'
            elif self.source_type == "HTTP":
                logger.info(f"Connecting to HTTP stream: {source_param}")
                self.cap = cv2.VideoCapture(source_param, cv2.CAP_FFMPEG)
            else:
                # USB camera or file
                logger.info(f"Connecting to {self.source_type} source: {source_param}")
                self.cap = cv2.VideoCapture(source_param)
            
            if not self.cap.isOpened():
                logger.error(f"Failed to open video source: {source_param}")
                return False
            
            # Set resolution for USB cameras (RTSP ignores this as stream determines resolution)
            if self.source_type == "USB":
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, buffer_size)
            
            # Test read to verify actual video data
            ret, test_frame = self.cap.read()
            if not ret or test_frame is None:
                logger.error("Failed to read test frame from source")
                self.cap.release()
                return False
            
            # Verify frame has real data
            if test_frame.max() <= 1:
                logger.error("Video source has no real data (blank frames)")
                self.cap.release()
                del test_frame
                return False
            
            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            
            logger.info(f"Video source connected: {actual_width}x{actual_height} @ {fps:.1f}fps")
            logger.info(f"Frame data range: {test_frame.min()}-{test_frame.max()}")
            
            del test_frame
            self.is_connected = True
            self.reconnect_attempts = 0
            self.last_frame_time = time.time()
            
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to video source: {e}")
            if self.cap:
                self.cap.release()
            return False
    
    def read(self) -> Tuple[bool, Optional[any]]:
        """
        Read a frame from the video source with automatic reconnection
        
        Returns:
            (success, frame) tuple
        """
        if not self.is_connected or self.cap is None:
            # Try to reconnect
            if self.reconnect_attempts < self.max_reconnect_attempts:
                logger.warning(f"Attempting to reconnect... (attempt {self.reconnect_attempts + 1}/{self.max_reconnect_attempts})")
                time.sleep(self.reconnect_delay)
                if self.connect():
                    self.reconnect_attempts = 0
                else:
                    self.reconnect_attempts += 1
                    return False, None
            else:
                logger.error(f"Max reconnection attempts ({self.max_reconnect_attempts}) reached")
                return False, None
        
        try:
            ret, frame = self.cap.read()
            
            if not ret or frame is None:
                logger.warning("Failed to read frame, marking as disconnected")
                self.is_connected = False
                return False, None
            
            # Check for frame timeout (stream might be frozen)
            current_time = time.time()
            if current_time - self.last_frame_time > self.frame_timeout:
                logger.warning(f"Frame timeout ({self.frame_timeout}s), reconnecting...")
                self.is_connected = False
                self.cap.release()
                return False, None
            
            self.last_frame_time = current_time
            return True, frame
            
        except cv2.error as e:
            logger.error(f"OpenCV error reading frame: {e}")
            self.is_connected = False
            return False, None
        except Exception as e:
            logger.error(f"Unexpected error reading frame: {e}")
            self.is_connected = False
            return False, None
    
    def release(self):
        """Release video source"""
        if self.cap:
            self.cap.release()
            self.is_connected = False
            logger.info(f"Video source released: {self.source}")
    
    def get_info(self) -> dict:
        """Get video source information"""
        if not self.is_connected or not self.cap:
            return {
                'source': self.source,
                'type': self.source_type,
                'connected': False
            }
        
        return {
            'source': self.source,
            'type': self.source_type,
            'connected': True,
            'width': int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'fps': self.cap.get(cv2.CAP_PROP_FPS),
            'reconnect_attempts': self.reconnect_attempts
        }
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.release()


def parse_video_source(source_str: str) -> str:
    """
    Parse and validate video source string
    
    Args:
        source_str: Source string (camera index, URL, or file path)
    
    Returns:
        Validated source string
    
    Examples:
        "0" -> 0 (USB camera)
        "rtsp://admin:pass@192.168.1.100:554/stream" -> RTSP URL
        "video.mp4" -> file path
    """
    # Strip whitespace
    source_str = source_str.strip()
    
    # Check if it's a camera index
    if source_str.isdigit():
        return int(source_str)
    
    # Check if it's a URL
    if any(source_str.lower().startswith(proto) for proto in ['rtsp://', 'rtmp://', 'http://', 'https://']):
        # Validate URL format
        try:
            parsed = urlparse(source_str)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError(f"Invalid URL format: {source_str}")
            return source_str
        except Exception as e:
            raise ValueError(f"Invalid video source URL: {e}")
    
    # Check if it's a file path
    if os.path.exists(source_str):
        return source_str
    
    # Default to camera index 0
    logger.warning(f"Could not parse video source '{source_str}', defaulting to camera 0")
    return 0


def test_video_source(source: str, duration: int = 5) -> bool:
    """
    Test a video source by attempting to read frames
    
    Args:
        source: Video source to test
        duration: Duration in seconds to test
    
    Returns:
        True if source works
    """
    logger.info(f"Testing video source: {source}")
    
    try:
        with VideoSource(source) as vs:
            if not vs.connect():
                logger.error("Failed to connect to video source")
                return False
            
            start_time = time.time()
            frame_count = 0
            
            while time.time() - start_time < duration:
                ret, frame = vs.read()
                if not ret:
                    logger.error("Failed to read frame during test")
                    return False
                frame_count += 1
                time.sleep(0.033)  # ~30fps
            
            fps = frame_count / duration
            logger.info(f"Video source test PASSED: {frame_count} frames in {duration}s ({fps:.1f} fps)")
            return True
            
    except Exception as e:
        logger.error(f"Video source test FAILED: {e}")
        return False


if __name__ == '__main__':
    # Test script
    logging.basicConfig(level=logging.INFO)
    
    import sys
    if len(sys.argv) > 1:
        source = sys.argv[1]
    else:
        source = "0"  # Default to USB camera 0
    
    print(f"\nTesting video source: {source}\n")
    test_video_source(source, duration=5)
