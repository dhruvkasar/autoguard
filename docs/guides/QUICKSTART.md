# AutoGuard - Quick Start Guide

## Prerequisites
- Docker & Docker Compose installed
- Webcam or IP camera (optional for demo)
- Python 3.10+ (for local development)

## Quick Start with Docker (Recommended)

### 1. Clone and Setup
```bash
cd "D:\Major Project"
cp .env.example .env
# Edit .env and add your Telegram bot token and chat IDs
```

### 2. Start Services
```bash
docker-compose up -d
```

### 3. Access Dashboard
Open browser: http://localhost:5000

Default login tokens (set in .env):
- Admin: `admin123` (full access)
- Security: `security123` (view evidence)
- Viewer: `viewer123` (read-only)

### 4. Stop Services
```bash
docker-compose down
```

## Local Development Setup

### 1. Create Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Configure Environment
```powershell
cp .env.example .env
# Edit .env with your settings
```

### 4. Run Backend Dashboard
```powershell
python -m src.server
# Access at http://localhost:5000
```

### 5. Run Detection (separate terminal)
```powershell
# Webcam
python src/main.py --source 0

# Video file
python src/main.py --source test_footage.mp4

# IP Camera (RTSP)
python src/main.py --source rtsp://username:password@192.168.1.100/stream
```

## Configuration

### Zone Calibration
```powershell
python -m src.zone_calibrator
# Draw zones on camera snapshot, copy coordinates to config/config.yaml
```

### Adjust Detection Thresholds
Edit `config/config.yaml`:
```yaml
rules:
  loitering_seconds: 30  # Increase for production (demo: 5)
  shelf_exit_repeat_count: 2
  shelf_exit_time_window_seconds: 60
```

### Telegram Alerts Setup
1. Create bot via @BotFather on Telegram
2. Get bot token (format: `1234567890:ABCdef...`)
3. Message your bot, then visit: `https://api.telegram.org/bot<TOKEN>/getUpdates`
4. Copy chat ID from response
5. Add to `.env`:
```
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_IDS=your_chat_id
```

## Verify Installation

### Evidence Integrity Check
```powershell
python -m src.verify_evidence --dir evidence
```

### System Health Check
```powershell
curl http://localhost:5000/health
# Response: {"status": "ok"}
```

## Project Structure
```
D:\Major Project\
├── src/                    # Source code
│   ├── main.py            # Detection entry point
│   ├── server.py          # Flask dashboard
│   ├── detector.py        # YOLOv8 wrapper
│   ├── tracker.py         # ByteTrack wrapper
│   ├── rules.py           # Behavior engine
│   ├── zones.py           # Zone management
│   ├── evidence.py        # Evidence storage
│   ├── alerts.py          # Alert dispatcher
│   └── description_generator.py  # AI descriptions
├── templates/             # Dashboard HTML templates
├── static/                # CSS/JS assets
├── config/                # Configuration files
├── evidence/              # Stored snapshots
├── logs/                  # Audit logs
├── tests/                 # Unit tests
├── docs/                  # Module documentation
├── docker-compose.yml     # Docker orchestration
├── Dockerfile             # Container image
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Troubleshooting

### Dashboard shows no evidence
- Run detection first: `python src/main.py --source 0`
- Trigger a rule by standing in shelf zone for 5+ seconds

### Telegram alerts not sending
- Check bot token in .env (no spaces)
- Check chat IDs are correct
- Verify internet connection
- Check logs: `tail -f logs/app.log`

### Camera not detected
- Windows: Check Device Manager for webcam
- Try different source numbers: `--source 1`, `--source 2`
- Check camera permissions (Windows Privacy Settings)

### Docker build fails
- Ensure Docker Desktop is running
- Check disk space (images are ~2GB)
- Try: `docker-compose build --no-cache`

## Features Implemented

✅ Person detection (YOLOv8)  
✅ Multi-object tracking (ByteTrack)  
✅ Zone-based behavior analysis  
✅ 3 theft detection rules  
✅ AI description generator  
✅ Evidence capture with SHA-256 integrity  
✅ Telegram instant alerts  
✅ Professional Bootstrap dashboard  
✅ Evidence viewer with thumbnails  
✅ Docker deployment  

## Planned Features (MVP Roadmap)

⚠️ Violence/threat detection (pose-based)  
⚠️ Mobile app (React Native)  
⚠️ Device pairing system  
⚠️ Evidence encryption (AES-256)  
⚠️ JWT authentication  
⚠️ Live camera feed in dashboard  

## License
Academic/Educational Use (B.Tech Final Year Project)

## Contact
For issues or questions, refer to project documentation in `docs/` directory.
