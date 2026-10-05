# AutoGuard - RTSP Stream Configuration Guide

## Overview

AutoGuard now supports multiple video source types:
- **USB Cameras** (default)
- **RTSP Streams** (IP cameras)
- **RTMP Streams** (live streaming)
- **HTTP Streams** (MJPEG, HLS)
- **Video Files** (for testing/replay)

## Quick Start

### 1. Using USB Camera (Default)

In `config/config.yaml`:
```yaml
video:
  source: 0  # Camera index (0, 1, 2, etc.)
```

Or via command line:
```bash
python -m src.main --source 0
```

### 2. Using RTSP Stream (IP Camera)

In `config/config.yaml`:
```yaml
video:
  source: "rtsp://192.168.1.100:554/stream"
  reconnect_delay: 5
  max_reconnect_attempts: 10
```

Or via command line:
```bash
python -m src.main --source "rtsp://192.168.1.100:554/stream"
```

### 3. Using Video File

```yaml
video:
  source: "videos/test_footage.mp4"
```

---

## RTSP URL Formats

### Common IP Camera RTSP URLs

**Generic Format:**
```
rtsp://[username]:[password]@[ip_address]:[port]/[stream_path]
```

**Examples by Brand:**

#### Hikvision
```
rtsp://admin:password@192.168.1.64:554/Streaming/Channels/101
rtsp://admin:password@192.168.1.64:554/Streaming/Channels/102  # Sub-stream
```

#### Dahua
```
rtsp://admin:password@192.168.1.108:554/cam/realmonitor?channel=1&subtype=0
rtsp://admin:password@192.168.1.108:554/cam/realmonitor?channel=1&subtype=1  # Sub-stream
```

#### Axis
```
rtsp://root:password@192.168.1.100/axis-media/media.amp
```

#### Foscam
```
rtsp://admin:password@192.168.1.100:554/videoMain
rtsp://admin:password@192.168.1.100:554/videoSub  # Sub-stream
```

#### Reolink
```
rtsp://admin:password@192.168.1.100:554/h264Preview_01_main
rtsp://admin:password@192.168.1.100:554/h264Preview_01_sub  # Sub-stream
```

#### TP-Link
```
rtsp://admin:password@192.168.1.100:554/stream1
rtsp://admin:password@192.168.1.100:554/stream2  # Sub-stream
```

#### Amcrest
```
rtsp://admin:password@192.168.1.100:554/cam/realmonitor?channel=1&subtype=0
```

---

## Configuration Options

### Basic Configuration

```yaml
video:
  source: "rtsp://admin:password@192.168.1.100:554/stream"
  width: 1280
  height: 720
  display: true
```

**Note:** For RTSP streams, `width` and `height` are informational. The actual resolution is determined by the camera stream.

### Advanced Configuration

```yaml
video:
  source: "rtsp://camera.local/stream"
  
  # Reconnection settings (important for network streams)
  reconnect_delay: 5              # Seconds to wait before reconnecting
  max_reconnect_attempts: 10      # Max reconnection attempts
  
  # Display settings
  display: true                   # Show video window
```

---

## Finding Your Camera's RTSP URL

### Method 1: Check Camera Documentation
- Look for "RTSP URL" or "Streaming URL" in the manual
- Common ports: 554 (RTSP), 8554 (alternative)

### Method 2: Use Camera Web Interface
1. Access camera's web interface (e.g., http://192.168.1.100)
2. Look in Settings → Network → Streaming
3. Copy the RTSP URL

### Method 3: Use ONVIF Device Manager
1. Download ONVIF Device Manager (free)
2. Scan network for cameras
3. View RTSP URLs for each discovered camera

### Method 4: Test Common URLs
Use the provided test script:
```bash
python test_rtsp.py 192.168.1.100
```

---

## Testing RTSP Connection

### Test Script

Create `test_rtsp.py`:
```python
from src.video_source import test_video_source
import sys

if len(sys.argv) < 2:
    print("Usage: python test_rtsp.py <rtsp_url>")
    print("Example: python test_rtsp.py rtsp://admin:pass@192.168.1.100:554/stream")
    sys.exit(1)

source = sys.argv[1]
print(f"\nTesting RTSP stream: {source}\n")

if test_video_source(source, duration=10):
    print("\n✅ RTSP stream test PASSED!")
    print("You can now use this URL in config.yaml")
else:
    print("\n❌ RTSP stream test FAILED!")
    print("Check:")
    print("1. Camera IP address and port")
    print("2. Username and password")
    print("3. Stream path")
    print("4. Network connectivity")
```

### Run Test
```bash
# Test with your RTSP URL
python test_rtsp.py "rtsp://admin:password@192.168.1.100:554/stream"
```

---

## Troubleshooting

### Connection Failed

**Symptoms:**
- "Failed to connect to RTSP source"
- Connection timeout

**Solutions:**
1. **Verify IP address:** Ping the camera
   ```bash
   ping 192.168.1.100
   ```

2. **Check port accessibility:** Use telnet
   ```bash
   telnet 192.168.1.100 554
   ```

3. **Verify credentials:** Try accessing via VLC:
   - Open VLC → Media → Open Network Stream
   - Enter RTSP URL
   - If VLC works, AutoGuard should work

4. **Firewall:** Ensure port 554 is not blocked

5. **Camera settings:** Enable RTSP in camera web interface

### Stream Freezes/Stutters

**Symptoms:**
- Video freezes periodically
- "Frame timeout" warnings

**Solutions:**
1. **Use sub-stream:** Lower resolution stream is more stable
   ```yaml
   source: "rtsp://admin:pass@192.168.1.100:554/stream2"  # Sub-stream
   ```

2. **Increase reconnect attempts:**
   ```yaml
   max_reconnect_attempts: 20
   reconnect_delay: 3
   ```

3. **Check network bandwidth:** RTSP requires stable network
   - Use wired connection instead of WiFi
   - Check for network congestion

4. **Camera buffer settings:** Reduce camera's encoding bitrate

### Authentication Errors

**Symptoms:**
- "401 Unauthorized"
- Connection refused

**Solutions:**
1. **URL encode special characters in password:**
   - `@` becomes `%40`
   - `#` becomes `%23`
   - Example: `admin:pass@word` → `admin:pass%40word`

2. **Try without credentials:**
   ```
   rtsp://192.168.1.100:554/stream
   ```

3. **Reset camera credentials** via web interface

### High Latency

**Symptoms:**
- Significant delay between real-time and displayed video

**Solutions:**
1. **Use TCP instead of UDP:**
   - AutoGuard automatically uses TCP for RTSP
   - More reliable but slightly higher latency

2. **Reduce camera buffer:**
   ```yaml
   buffer_size: 1  # Minimal buffering
   ```

3. **Use lower resolution sub-stream**

---

## Performance Optimization

### For Local Network Cameras

```yaml
video:
  source: "rtsp://admin:pass@192.168.1.100:554/stream"
  reconnect_delay: 2
  max_reconnect_attempts: 5
```

### For Remote/Cloud Cameras

```yaml
video:
  source: "rtsp://camera.cloud.com:554/stream"
  reconnect_delay: 10
  max_reconnect_attempts: 20
```

### For Unreliable Networks

```yaml
video:
  source: "rtsp://192.168.1.100:554/sub_stream"  # Use sub-stream
  reconnect_delay: 5
  max_reconnect_attempts: 100  # Keep trying
```

---

## Multi-Camera Setup (Coming in v1.5)

**Preview Configuration:**
```yaml
cameras:
  - name: "Entrance"
    source: "rtsp://192.168.1.100:554/stream"
  - name: "Checkout"
    source: "rtsp://192.168.1.101:554/stream"
  - name: "Exit"
    source: 1  # USB camera
```

---

## Security Best Practices

### 1. Use Strong Credentials
```yaml
# ❌ BAD
source: "rtsp://admin:admin@192.168.1.100:554/stream"

# ✅ GOOD
source: "rtsp://admin:Str0ng_P@ssw0rd@192.168.1.100:554/stream"
```

### 2. Use .env for Credentials
```yaml
# config.yaml
video:
  source: "${RTSP_URL}"
```

```bash
# .env
RTSP_URL=rtsp://admin:password@192.168.1.100:554/stream
```

### 3. Use VPN for Remote Access
- Don't expose RTSP ports to the internet
- Use VPN or SSH tunnel

### 4. Change Default Ports
- Use non-standard port instead of 554
- Configure in camera settings

---

## Examples

### Example 1: Retail Store with IP Camera

```yaml
video:
  source: "rtsp://admin:store2024@192.168.1.64:554/Streaming/Channels/101"
  display: true
  reconnect_delay: 5
  max_reconnect_attempts: 10

alerts:
  camera_id: "STORE_ENTRANCE"
  enabled: true
```

### Example 2: Testing with Video File

```yaml
video:
  source: "test_footage/retail_test.mp4"
  display: true
```

### Example 3: Remote Camera via Public IP

```yaml
video:
  source: "rtsp://admin:pass@203.0.113.100:8554/live"
  reconnect_delay: 10
  max_reconnect_attempts: 20
```

---

## Common RTSP Ports

| Port | Purpose |
|------|---------|
| 554  | Standard RTSP port |
| 8554 | Alternative RTSP port |
| 7447 | Some cameras (TP-Link) |
| 88   | Some cameras (Reolink) |

---

## Supported Protocols

| Protocol | Support | Use Case |
|----------|---------|----------|
| RTSP     | ✅ Full | IP cameras, NVRs |
| RTMP     | ✅ Full | Live streaming servers |
| HTTP/MJPEG | ✅ Full | Web cameras |
| HLS (m3u8) | ⚠️ Limited | Cloud streams |
| USB      | ✅ Full | Local webcams |
| Files    | ✅ Full | Testing/replay |

---

## Getting Help

If you're having issues:

1. **Test with VLC Media Player first**
   - If VLC can't connect, AutoGuard won't either
   
2. **Check camera documentation**
   - Look for RTSP URL format
   
3. **Use the test script**
   ```bash
   python test_rtsp.py "your_rtsp_url"
   ```

4. **Check logs**
   ```bash
   cat logs/autoguard_*.log
   ```

---

## Version History

- **v1.1.0** (2026-09-26): Added RTSP stream support
- **v1.0.0** (2026-08-28): Initial release (USB only)

---

## Next Features (v1.5)

- Multi-camera support
- Camera management web UI
- ONVIF device discovery
- Automatic RTSP URL detection
- Stream recording/playback

---

**Need more help?** Check the main README.md or open an issue on GitHub.
