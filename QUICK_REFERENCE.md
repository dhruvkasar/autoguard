# 🎯 AutoGuard - Quick Access Guide

**Version:** 1.1.0  
**Last Updated:** October 5, 2026  
**Status:** Production Ready ✅

---

## ⚡ Quick Commands

### Start AutoGuard
```bash
# Detection Engine
python -m src.main

# Web Dashboard
python -m src.server

# Or use shortcuts
start.bat              # Detection
start_dashboard.bat    # Dashboard
```

### Testing & Setup
```bash
# Find cameras
python tools/discover_cameras.py

# Test Telegram
python tools/check_telegram.py

# Test RTSP stream
python tools/test_rtsp.py "rtsp://camera-url"

# Migrate to database
python tools/migrate_to_database.py
```

---

## 📁 Important Files

| File | Purpose | Location |
|------|---------|----------|
| **Configuration** | System settings | `config/config.yaml` |
| **Environment** | Secrets & tokens | `.env` |
| **Main README** | Project overview | `README.md` |
| **Quick Start** | Get started fast | `docs/guides/QUICKSTART_v1.1.md` |
| **Structure** | Project organization | `PROJECT_STRUCTURE.md` |

---

## 📚 Documentation Index

### Setup Guides
- **Quick Start:** `docs/guides/QUICKSTART_v1.1.md`
- **Telegram Setup:** `docs/guides/TELEGRAM_SETUP.md` (10 min)
- **RTSP Setup:** `docs/guides/RTSP_GUIDE.md` (IP cameras)
- **Deployment:** `docs/guides/DEPLOYMENT_GUIDE.md`

### Reference
- **API Documentation:** `docs/API.md`
- **Security Guide:** `docs/SECURITY.md`
- **Project Roadmap:** `PROJECT_PROGRESS.md`
- **Git Guide:** `docs/guides/GITHUB_PUSH_GUIDE.md`

---

## 🔧 Configuration

### Your Current Setup
```yaml
Camera: USB Index 1 (1280x720 @ 27.2 fps) ✅
Telegram: @Your_autoguard_Bot ✅
Database: JSON mode (SQLite ready)
CSRF: Enabled ✅
RTSP: Ready for IP cameras
```

### Key Settings
```bash
# .env
TELEGRAM_BOT_TOKEN=8934910583:AAHsJjKi2...
TELEGRAM_CHAT_IDS=5126953976
CAMERA_ID=ENTRANCE_CAM
USE_DATABASE=false

# config/config.yaml
video:
  source: 1
alerts:
  cooldown_seconds: 15
  daily_cap: 50
```

---

## 🛠️ Common Tasks

### Change Camera
```yaml
# config/config.yaml
video:
  source: 0              # USB camera 0
  # or
  source: "rtsp://..."  # IP camera
```

### Adjust Alert Frequency
```yaml
# config/config.yaml
alerts:
  cooldown_seconds: 5   # More alerts
  cooldown_seconds: 30  # Fewer alerts
```

### Enable Database
```bash
# 1. Migrate existing data
python tools/migrate_to_database.py

# 2. Enable in .env
USE_DATABASE=true

# 3. Restart server
python -m src.server
```

### Calibrate Zones
```bash
calibrate_zones.bat
# or
python -m src.zone_calibrator
```

---

## 📱 Access Points

### Web Dashboard
```
URL: http://localhost:5000
Login: Use token from .env file
```

### Telegram Bot
```
Bot: @Your_autoguard_Bot
Status: ✅ Working
```

### Evidence
```
Location: evidence/
Web: http://localhost:5000/dashboard
```

---

## 🆘 Troubleshooting

### Camera Issues
```bash
# Find working cameras
python tools/discover_cameras.py

# Test specific camera
python tools/test_rtsp.py 1
```

### Telegram Not Working
```bash
# Check configuration
python tools/check_telegram.py

# Get diagnostics
python tools/diagnose_telegram.py
```

### Web Dashboard Issues
```bash
# Check if FLASK_SECRET_KEY is set
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('Key set:', bool(os.getenv('FLASK_SECRET_KEY')))"

# Regenerate key
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 📊 Project Structure

```
AutoGuard/
├── src/           # Source code (17 modules)
├── tools/         # Utility scripts (9 tools)
├── docs/          # Documentation (18 files)
│   ├── guides/    # How-to guides
│   └── architecture/  # System diagrams
├── config/        # Configuration files
├── evidence/      # Incident photos & data
├── data/          # SQLite database
├── templates/     # Web dashboard HTML
└── tests/         # Unit tests
```

**Full details:** See `PROJECT_STRUCTURE.md`

---

## ✨ Features Status

| Feature | Status | Version |
|---------|--------|---------|
| Person Detection | ✅ Working | v1.0.0 |
| Behavioral Rules | ✅ Active (3 rules) | v1.0.0 |
| Evidence Storage | ✅ JSON/Database | v1.1.0 |
| Telegram Alerts | ✅ Configured | v1.0.0 |
| Web Dashboard | ✅ CSRF Protected | v1.1.0 |
| RTSP Support | ✅ Ready | v1.1.0 |
| Database | ✅ Available | v1.1.0 |

---

## 🔗 Quick Links

| Resource | Link |
|----------|------|
| **GitHub** | https://github.com/dhruvkasar/autoguard |
| **Telegram Bot** | https://t.me/Your_autoguard_Bot |
| **Dashboard** | http://localhost:5000 |

---

## 📞 Getting Help

1. **Check docs:** `docs/guides/` directory
2. **See structure:** `PROJECT_STRUCTURE.md`
3. **Read README:** `README.md`
4. **Check progress:** `PROJECT_PROGRESS.md`
5. **GitHub Issues:** Report bugs/requests

---

## 🎯 Next Steps

**New User?**
1. Read: `docs/guides/QUICKSTART_v1.1.md`
2. Setup Telegram: `docs/guides/TELEGRAM_SETUP.md`
3. Run: `python -m src.main`

**Need Camera Help?**
1. Run: `python tools/discover_cameras.py`
2. Read: `docs/guides/RTSP_GUIDE.md`

**Want Database?**
1. Run: `python tools/migrate_to_database.py`
2. Set: `USE_DATABASE=true` in `.env`

---

**Current Time:** October 5, 2026 at 9:51 PM (IST)  
**Your System:** Fully Operational ✅  
**Ready to Use:** YES! 🚀

---

*Keep this file for quick reference!*
