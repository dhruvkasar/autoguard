"""
Test script to verify stream manager is working
"""
import cv2
import time
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.stream_manager import get_stream_manager

print("Testing Stream Manager...")
print("=" * 50)

stream_mgr = get_stream_manager()

# Check initial status
stats = stream_mgr.get_stats()
print(f"\nInitial Status:")
print(f"  Active: {stats['active']}")
print(f"  Has Frame: {stats['has_frame']}")
print(f"  Clients: {stats['clients']}")
print(f"  Last Update: {stats['last_update']}")

# Create a test frame
print("\nCreating test frame...")
test_frame = cv2.imread("yolov8n.pt") if os.path.exists("yolov8n.pt") else None

if test_frame is None:
    # Create a colored test pattern
    test_frame = cv2.imread("evidence/evidence_CAM01_id4_Loitering_in_Shelf_Zone_20260205-223754.jpg") if os.path.exists("evidence/evidence_CAM01_id4_Loitering_in_Shelf_Zone_20260205-223754.jpg") else None

if test_frame is None:
    # Create synthetic test frame
    import numpy as np
    test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(test_frame, "TEST FRAME", (200, 240),
               cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
    cv2.putText(test_frame, f"Time: {time.strftime('%H:%M:%S')}", (180, 300),
               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

print(f"Test frame shape: {test_frame.shape}")

# Push frame to stream manager
print("\nPushing frame to stream manager...")
stream_mgr.update_frame(test_frame)

# Wait a bit
time.sleep(0.5)

# Check status again
stats = stream_mgr.get_stats()
print(f"\nAfter Update:")
print(f"  Active: {stats['active']}")
print(f"  Has Frame: {stats['has_frame']}")
print(f"  Clients: {stats['clients']}")
print(f"  Last Update: {stats['last_update']}")

# Try to retrieve frame
print("\nRetrieving frame from stream manager...")
retrieved_frame = stream_mgr.get_frame()
print(f"Retrieved frame shape: {retrieved_frame.shape}")

# Check if files were created
print(f"\nChecking stream_cache directory...")
import os
if os.path.exists("stream_cache/latest_frame.jpg"):
    size = os.path.getsize("stream_cache/latest_frame.jpg")
    print(f"  ✓ latest_frame.jpg exists ({size} bytes)")
else:
    print(f"  ✗ latest_frame.jpg NOT found")

if os.path.exists("stream_cache/frame_meta.json"):
    print(f"  ✓ frame_meta.json exists")
    with open("stream_cache/frame_meta.json", 'r') as f:
        print(f"  Content: {f.read()}")
else:
    print(f"  ✗ frame_meta.json NOT found")

print("\n" + "=" * 50)
print("Stream manager test complete!")
print("\nIf you see ✓ marks above, the stream manager is working.")
print("Now restart both start.bat and start_dashboard.bat")
