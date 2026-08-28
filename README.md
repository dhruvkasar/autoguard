# AutoGuard - AI-Powered Retail Security System

**Version:** 1.0.0 (MVP)  
**Status:** Production Ready  
**License:** MIT  

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Security: Yes](https://img.shields.io/badge/security-audited-green.svg)](./docs/SECURITY.md)
[![Tests: Passing](https://img.shields.io/badge/tests-passing-brightgreen.svg)](./tests/)

---

## 🎯 Overview

**AutoGuard** is a real-time AI-powered surveillance system designed for retail environments. It uses computer vision to detect suspicious behaviors such as theft, loitering, and potential security threats while maintaining privacy and security best practices.

Developed by cybersecurity students with a focus on secure-by-design principles.

### Key Features

✅ **Real-time Person Detection & Tracking** - YOLOv8 + ByteTrack  
✅ **Behavioral Analysis** - Loitering, repeated movements, exit without checkout  
✅ **Evidence Capture** - Automatic snapshots with SHA-256 integrity verification  
✅ **Secure Web Dashboard** - Role-based access control (Admin, Security, Viewer)  
✅ **Mobile Alerts** - Telegram integration with secure token authentication  
✅ **Live Video Streaming** - Real-time feed with activity statistics  
✅ **AI-Generated Descriptions** - Natural language incident reports  
✅ **Audit Logging** - Complete audit trail of all detections and actions  

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** (3.11 recommended)
- **Webcam or IP Camera**
- **Windows 10/11** (or Linux/macOS with minor adjustments)
- **4GB RAM minimum** (8GB recommended)

### Installation

**1. Clone or Extract Project**
```powershell
cd D:\
# Extract AutoGuard_Transfer.zip here
cd AutoGuard
```

**2. Create Virtual Environment**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**3. Install Dependencies**
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

**4. Configure Environment**
```powershell
# Copy example env file
Copy-Item .env.example .env

# Edit .env and set your tokens
notepad .env
```

**Generate secure tokens:**
```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**5. Test Camera**
```powershell
python test_camera.py
```

**6. Calibrate Zones (First Time)**
```powershell
python -m src.zone_calibrator
# Draw shelf, checkout, and exit zones
# Press 's' to save, 'q' to quit
```

**7. Run Detection**
```powershell
python src/main.py --source 0
```

**8. Start Web Dashboard**
```powershell
# In a new terminal
.\.venv\Scripts\Activate.ps1
python -m flask --app src.server run --host 127.0.0.1 --port 5000
```

Open browser: **http://localhost:5000**

---

## 📁 Project Structure

```
AutoGuard/
├── src/                          # Source code
│   ├── main.py                   # Main detection pipeline
│   ├── server.py                 # Flask web server & API
│   ├── detector.py               # YOLO object detection
│   ├── tracker.py                # ByteTrack person tracking
│   ├── zones.py                  # Zone management
│   ├── rules.py                  # Behavioral rules engine
│   ├── evidence.py               # Evidence capture & storage
│   ├── alerts.py                 # Telegram alerting
│   ├── description_generator.py  # AI description templates
│   ├── stream_manager.py         # Live video streaming
│   ├── activity_tracker.py       # Real-time statistics
│   ├── zone_calibrator.py        # Interactive zone setup
│   ├── verify_evidence.py        # SHA-256 integrity verification
│   ├── utils.py                  # Utility functions
│   ├── config_loader.py          # Configuration management
│   └── logging_config.py         # Logging setup
│
├── config/                       # Configuration files
│   └── config.yaml               # Main configuration
│
├── templates/                    # HTML templates
│   ├── dashboard.html            # Main dashboard
│   ├── live.html                 # Live feed viewer
│   └── devices.html              # Device management
│
├── static/                       # Static web assets
│   ├── css/                      # Stylesheets
│   └── js/                       # JavaScript
│
├── tests/                        # Unit tests
│   └── test_rules.py             # Behavioral rules tests
│
├── evidence/                     # Evidence storage (generated)
├── logs/                         # Application logs (generated)
├── docs/                         # Documentation
│
├── .env                          # Environment variables (secrets)
├── .env.example                  # Example environment file
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Docker configuration
├── docker-compose.yml            # Docker Compose setup
├── README.md                     # This file
├── test_camera.py                # Camera testing utility
└── yolov8n.pt                    # YOLO model weights
```

---

## ⚙️ Configuration

### Environment Variables (.env)

```env
# Telegram Alerts
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_IDS=123456789,987654321
CAMERA_ID=CAM01

# Web Dashboard Authentication
ADMIN_TOKEN=generate_secure_token_here
SECURITY_TOKEN=generate_secure_token_here
VIEWER_TOKEN=generate_secure_token_here
```

### Main Configuration (config/config.yaml)

```yaml
# Detection Model
model:
  weights: yolov8n.pt
  confidence_threshold: 0.35
  device: auto  # auto, cpu, or cuda

# Behavioral Rules
rules:
  loitering_seconds: 5
  shelf_exit_repeat_count: 2
  shelf_exit_time_window_seconds: 60

# Zones (calibrate with zone_calibrator.py)
zones:
  shelf: [22, 28, 199, 454]
  checkout: [280, 51, 393, 446]
  exit: [544, 54, 611, 473]

# Video Source
video:
  source: 0  # 0=webcam, 1=external camera, or rtsp://...
  width: 640
  height: 480

# Storage
storage:
  evidence_dir: evidence
  logs_dir: logs
  retention_days: 7  # Auto-delete old evidence
```

---

## 🔐 Security Features

### Authentication & Authorization
- **Role-based access control** (Admin, Security, Viewer)
- **Secure token authentication** with constant-time comparison
- **HTTPOnly cookies** with SameSite protection
- **No tokens in URLs** (headers/cookies only)

### Data Protection
- **SHA-256 hash verification** for all evidence files
- **Path traversal protection** with strict filename validation
- **Security headers** (CSP, X-Frame-Options, HSTS)
- **Environment-based secrets** (never committed to code)

### Infrastructure Security
- **Docker runs as non-root** user
- **Minimal attack surface** (only necessary ports exposed)
- **Audit logging** of all security events
- **Evidence integrity verification** tool included

See [docs/SECURITY.md](./docs/SECURITY.md) for full security documentation.

---

## 📊 Web Dashboard

### Features

**Dashboard Overview**
- Total incidents counter
- High-priority alerts (violence/threats)
- Theft alerts counter
- Resolved incidents tracker
- Filterable evidence list with thumbnails

**Live Feed**
- Real-time video streaming (~30 FPS)
- Active person tracking
- Zone overlays
- Detection statistics

**Evidence Management**
- Download individual images
- Bulk export to ZIP
- Mark incidents as resolved
- AI-generated descriptions

### API Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/` | GET | - | Redirect to dashboard or login |
| `/login` | GET/POST | - | Authentication |
| `/dashboard` | GET | All | Main dashboard view |
| `/live` | GET | All | Live video feed |
| `/evidence` | GET | All | List evidence (JSON) |
| `/evidence/image?name=X` | GET | Admin/Security | Get evidence image |
| `/evidence/export` | GET | Admin/Security | Export all evidence (ZIP) |
| `/evidence/<id>/resolve` | POST | Admin/Security | Mark resolved |
| `/snapshot` | GET | All | Capture snapshot |
| `/health` | GET | - | Health check |

---

## 🧪 Testing

### Run Unit Tests
```powershell
python -m unittest discover tests
```

### Test Camera
```powershell
python test_camera.py
```

### Verify Evidence Integrity
```powershell
python -m src.verify_evidence --dir evidence
```

### Test Detection Pipeline
```powershell
# Test with video file
python src/main.py --source path/to/test_video.mp4
```

---

## 🐳 Docker Deployment

### Build and Run
```powershell
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Access
- **Dashboard:** http://localhost:5000
- **Health Check:** http://localhost:5000/health

---

## 🛠️ Development

### Code Style
- Follow PEP 8 guidelines
- Use type hints where applicable
- Document all functions with docstrings

### Adding New Rules
1. Edit `src/rules.py` - Add rule logic
2. Edit `src/description_generator.py` - Add description template
3. Add tests in `tests/test_rules.py`

### Extending the System
- **New zones:** Use zone calibrator tool
- **New alerts:** Extend `TelegramAlerter` class
- **New detection models:** Replace in `detector.py`
- **New UI features:** Edit templates and add routes in `server.py`

---

## 📈 Performance

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | Dual-core 2.0 GHz | Quad-core 3.0 GHz |
| RAM | 4 GB | 8 GB |
| Storage | 10 GB | 50 GB (for evidence) |
| Camera | 640x480 @ 15fps | 1280x720 @ 30fps |

### Optimization Tips
- Use GPU acceleration (CUDA) for faster detection
- Reduce video resolution for better performance
- Adjust `confidence_threshold` to reduce false positives
- Enable evidence retention to auto-delete old files

---

## 🐛 Troubleshooting

### Common Issues

**Camera not opening**
```powershell
# Try different camera indices
python src/main.py --source 1
python src/main.py --source 2

# Check if camera is in use by other apps
```

**Import errors**
```powershell
# Ensure virtual environment is activated
.\.venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Port 5000 already in use**
```powershell
# Use different port
python -m flask --app src.server run --port 5001
```

**Login not working (HTTPS redirect)**
```powershell
# For local demo, edit src/server.py line 125
# Remove secure=True parameter temporarily
```

See [docs/TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md) for more solutions.

---

## 📚 Documentation

- **[Installation Guide](./QUICKSTART.md)** - Detailed setup instructions
- **[Security Documentation](./docs/SECURITY.md)** - Security features and audit
- **[Deployment Guide](./DEPLOYMENT_GUIDE.md)** - How to deploy to other systems
- **[API Reference](./docs/API.md)** - Complete API documentation
- **[Architecture](./docs/ARCHITECTURE.md)** - System design and components

---

## 🤝 Contributing

This is an academic/educational project. Contributions are welcome!

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 👥 Authors

**AutoGuard Team**  
Cybersecurity Students  
Major Project 2026

---

## 🙏 Acknowledgments

- **Ultralytics** - YOLOv8 object detection
- **Supervision** - Computer vision tools
- **ByteTrack** - Multi-object tracking
- **Flask** - Web framework
- **OpenCV** - Computer vision library

---

## 📧 Support

For issues, questions, or feature requests:
- Create an issue on GitHub
- Email: [your-email@example.com]
- Documentation: [./docs/](./docs/)

---

## 🔄 Version History

### v1.0.0 (2026-08-28)
- ✅ Initial release
- ✅ Real-time detection pipeline
- ✅ Web dashboard with live streaming
- ✅ Role-based authentication
- ✅ Evidence capture with integrity verification
- ✅ Telegram alerts
- ✅ Security hardening completed
- ✅ Docker support

---

**Made with ❤️ for a safer retail environment**
