"""
Test script for RTSP stream connectivity
Tests video sources before using them in AutoGuard
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.video_source import test_video_source, parse_video_source
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def print_banner():
    print("\n" + "="*60)
    print("AutoGuard - RTSP Stream Test Utility")
    print("="*60 + "\n")

def print_examples():
    print("Examples:")
    print("  USB Camera:")
    print("    python test_rtsp.py 0")
    print("\n  RTSP Stream:")
    print("    python test_rtsp.py rtsp://admin:pass@192.168.1.100:554/stream")
    print("\n  Video File:")
    print("    python test_rtsp.py test_video.mp4")
    print("\n  Common RTSP URLs by brand:")
    print("    Hikvision: rtsp://admin:pass@192.168.1.64:554/Streaming/Channels/101")
    print("    Dahua:     rtsp://admin:pass@192.168.1.108:554/cam/realmonitor?channel=1&subtype=0")
    print("    Reolink:   rtsp://admin:pass@192.168.1.100:554/h264Preview_01_main")
    print()

def main():
    print_banner()
    
    if len(sys.argv) < 2:
        print("Usage: python test_rtsp.py <video_source>")
        print()
        print_examples()
        sys.exit(1)
    
    source = sys.argv[1]
    duration = 10  # Test for 10 seconds
    
    if len(sys.argv) > 2:
        try:
            duration = int(sys.argv[2])
        except ValueError:
            print(f"Warning: Invalid duration '{sys.argv[2]}', using default 10 seconds")
    
    print(f"Video Source: {source}")
    print(f"Test Duration: {duration} seconds")
    print()
    
    # Parse and validate source
    try:
        parsed_source = parse_video_source(source)
        print(f"Parsed Source: {parsed_source}")
        print()
    except Exception as e:
        print(f"❌ Error parsing video source: {e}")
        sys.exit(1)
    
    # Run test
    print("Starting connection test...")
    print("-" * 60)
    
    success = test_video_source(parsed_source, duration=duration)
    
    print("-" * 60)
    print()
    
    if success:
        print("TEST PASSED!")
        print()
        print("Next steps:")
        print("1. Add this source to config/config.yaml:")
        print(f"   video:")
        print(f"     source: {source}")
        print()
        print("2. Or use command line:")
        print(f"   python -m src.main --source {source}")
        print()
        return 0
    else:
        print("TEST FAILED!")
        print()
        print("Troubleshooting:")
        print("1. Check camera IP address and port")
        print("2. Verify username and password")
        print("3. Ensure RTSP is enabled on camera")
        print("4. Test with VLC Media Player first")
        print("5. Check network connectivity (ping camera IP)")
        print("6. Try sub-stream URL if main stream fails")
        print()
        print("See RTSP_GUIDE.md for detailed troubleshooting")
        print()
        return 1

if __name__ == '__main__':
    sys.exit(main())
