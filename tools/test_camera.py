"""
Simple camera test script to verify camera is working
"""
import cv2
import time

print("Testing camera access...")
print("=" * 50)

# Try different camera indices
for camera_idx in [0, 1, 2]:
    print(f"\nTrying camera index {camera_idx}...")
    cap = cv2.VideoCapture(camera_idx)
    
    if not cap.isOpened():
        print(f"  ❌ Camera {camera_idx} failed to open")
        continue
    
    print(f"  ✓ Camera {camera_idx} opened successfully")
    
    # Try to read a frame
    ret, frame = cap.read()
    if not ret or frame is None:
        print(f"  ❌ Camera {camera_idx} opened but cannot read frames")
        cap.release()
        continue
    
    print(f"  ✓ Frame captured: {frame.shape[1]}x{frame.shape[0]} pixels")
    print(f"  ✓ Frame type: {frame.dtype}, min={frame.min()}, max={frame.max()}")
    
    # Display the frame
    print(f"\n  Opening video window for camera {camera_idx}...")
    print("  Press 'q' to close and try next camera, or wait 10 seconds")
    
    start_time = time.time()
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("  ❌ Failed to read frame during display")
            break
        
        frame_count += 1
        
        # Add info overlay
        cv2.putText(frame, f"Camera {camera_idx} - Frame {frame_count}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, "Press 'q' to quit", 
                   (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        cv2.imshow(f"Camera Test - Index {camera_idx}", frame)
        
        # Check for quit or timeout
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print(f"\n  User pressed 'q' - closing camera {camera_idx}")
            break
        
        if time.time() - start_time > 10:
            print(f"\n  10 second timeout - closing camera {camera_idx}")
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print(f"  Camera {camera_idx} test complete")

print("\n" + "=" * 50)
print("Camera test finished")
print("\nIf you saw video feed above, your camera is working!")
print("If you only saw a black screen, there may be a:")
print("  1. Camera permission issue")
print("  2. Camera driver issue")
print("  3. Another app is using the camera")
