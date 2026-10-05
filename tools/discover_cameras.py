"""
Camera Discovery Utility for AutoGuard
Scans for available cameras and tests which ones work
"""

import cv2
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.video_source import VideoSource

def print_banner():
    print("\n" + "="*60)
    print("AutoGuard - Camera Discovery Utility")
    print("="*60 + "\n")

def test_camera_index(index):
    """Test a specific camera index"""
    try:
        vs = VideoSource(index)
        if vs.connect(width=640, height=480):
            info = vs.get_info()
            vs.release()
            return True, info
        vs.release()
        return False, None
    except Exception as e:
        return False, None

def discover_cameras(max_cameras=10):
    """Discover all available cameras"""
    print("Scanning for cameras (this may take a minute)...\n")
    
    working_cameras = []
    
    for i in range(max_cameras):
        print(f"Testing camera index {i}... ", end="", flush=True)
        
        success, info = test_camera_index(i)
        
        if success:
            print("FOUND!")
            print(f"   Resolution: {info['width']}x{info['height']}")
            print(f"   FPS: {info['fps']:.1f}")
            print(f"   Type: {info['type']}")
            working_cameras.append(i)
        else:
            print("Not available")
    
    return working_cameras

def main():
    print_banner()
    
    # Discover cameras
    cameras = discover_cameras(max_cameras=5)
    
    print("\n" + "="*60)
    print("DISCOVERY RESULTS")
    print("="*60)
    
    if cameras:
        print(f"\nFound {len(cameras)} working camera(s):")
        for cam in cameras:
            print(f"   - Camera index: {cam}")
        
        print("\n" + "-"*60)
        print("Next steps:")
        print("-"*60)
        print("\n1. Test a specific camera:")
        for cam in cameras:
            print(f"   python test_rtsp.py {cam}")
        
        print("\n2. Use in AutoGuard config.yaml:")
        print(f"   video:")
        print(f"     source: {cameras[0]}  # Use first working camera")
        
        print("\n3. Or use command line:")
        print(f"   python -m src.main --source {cameras[0]}")
        print()
    else:
        print("\nNo working cameras found!")
        print("\nPossible reasons:")
        print("1. No camera is connected")
        print("2. Camera is being used by another application")
        print("   (Close Zoom, Teams, Skype, etc.)")
        print("3. Camera permissions not granted")
        print("4. Camera drivers not installed")
        print("\nTroubleshooting:")
        print("- Check Device Manager (Windows)")
        print("- Close all apps that might use camera")
        print("- Try unplugging and reconnecting camera")
        print("- Restart computer")
        print()
        
        # Suggest RTSP or video file
        print("Alternatives:")
        print("1. Use an IP camera with RTSP:")
        print("   python test_rtsp.py \"rtsp://camera-url\"")
        print("\n2. Use a video file for testing:")
        print("   python test_rtsp.py \"video.mp4\"")
        print()

if __name__ == '__main__':
    main()
