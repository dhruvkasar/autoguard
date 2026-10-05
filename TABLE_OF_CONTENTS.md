# 📋 AutoGuard - Table of Contents

**Version:** 1.1.0  
**Date:** October 5, 2026  
**Status:** Production Ready

---

## 🚀 Getting Started

### Essential Reading
1. **[README.md](README.md)** - Project overview and features
2. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick commands and access
3. **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Complete project organization
4. **[docs/guides/QUICKSTART_v1.1.md](docs/guides/QUICKSTART_v1.1.md)** - Get started in 10 minutes

### First Time Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Configure `.env` file (see `.env.example`)
3. Setup Telegram: **[docs/guides/TELEGRAM_SETUP.md](docs/guides/TELEGRAM_SETUP.md)**
4. Find your camera: `python tools/discover_cameras.py`
5. Start detection: `python -m src.main`

---

## 📚 Documentation Hub

### User Guides (docs/guides/)

#### Quick Start Guides
- **[QUICKSTART.md](docs/guides/QUICKSTART.md)** - Original quick start (v1.0)
- **[QUICKSTART_v1.1.md](docs/guides/QUICKSTART_v1.1.md)** - Latest quick start (v1.1) ⭐

#### Telegram Setup (10 minutes)
- **[TELEGRAM_QUICKSTART.md](docs/guides/TELEGRAM_QUICKSTART.md)** - Quick 3-step setup ⭐
- **[TELEGRAM_SETUP.md](docs/guides/TELEGRAM_SETUP.md)** - Detailed guide with examples
- **[TELEGRAM_FIX.md](docs/guides/TELEGRAM_FIX.md)** - Troubleshooting "chat not found"

#### RTSP & IP Cameras
- **[RTSP_GUIDE.md](docs/guides/RTSP_GUIDE.md)** - Complete RTSP configuration ⭐
- **[RTSP_TEST_RESULTS.md](docs/guides/RTSP_TEST_RESULTS.md)** - Implementation verification

#### Deployment
- **[DEPLOYMENT_GUIDE.md](docs/guides/DEPLOYMENT_GUIDE.md)** - Deploy to team/production
- **[DEPLOYMENT_SUMMARY.md](docs/guides/DEPLOYMENT_SUMMARY.md)** - v1.1.0 deployment notes

#### Git & GitHub
- **[GITHUB_PUSH_GUIDE.md](docs/guides/GITHUB_PUSH_GUIDE.md)** - Push to GitHub
- **[GIT_PUSH_COMMANDS.md](docs/guides/GIT_PUSH_COMMANDS.md)** - Git commands reference

### Technical Documentation (docs/)
- **[docs/API.md](docs/API.md)** - REST API endpoint reference
- **[docs/SECURITY.md](docs/SECURITY.md)** - Security features and best practices
- **[docs/architecture/](docs/architecture/)** - System architecture diagrams

### Project Management
- **[PROJECT_PROGRESS.md](PROJECT_PROGRESS.md)** - Development roadmap & status
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Complete file organization ⭐
- **[LICENSE](LICENSE)** - MIT License

---

## 🔧 Tools & Scripts (tools/)

### Camera Tools
```bash
python tools/discover_cameras.py      # Find all available cameras
python tools/test_camera.py          # Test USB camera
python tools/test_rtsp.py <url>      # Test RTSP stream
python tools/test_stream.py          # Test video stream
```

### Telegram Tools
```bash
python tools/check_telegram.py       # Quick Telegram check ⭐
python tools/test_telegram.py        # Send test alert
python tools/diagnose_telegram.py    # Full diagnostics
python tools/get_telegram_chat_id.py # Get your chat ID
```

### Database Tools
```bash
python tools/migrate_to_database.py  # Migrate JSON to SQLite
```

---

## ⚙️ Configuration Files

### Core Configuration
- **[.env](.env)** - Environment variables (secrets, tokens)
- **[.env.example](.env.example)** - Environment template
- **[config/config.yaml](config/config.yaml)** - System configuration

### Docker
- **[Dockerfile](Dockerfile)** - Container configuration
- **[docker-compose.yml](docker-compose.yml)** - Stack orchestration

### Startup Scripts (Windows)
- **[start.bat](start.bat)** - Start detection engine
- **[start_dashboard.bat](start_dashboard.bat)** - Start web dashboard
- **[calibrate_zones.bat](calibrate_zones.bat)** - Calibrate detection zones

---

## 💻 Source Code (src/)

### Core Modules
- **[main.py](src/main.py)** - Detection engine entry point (469 lines)
- **[server.py](src/server.py)** - Web dashboard server (566 lines)

### Detection & Tracking
- **[detector.py](src/detector.py)** - YOLOv8 person detection
- **[tracker.py](src/tracker.py)** - ByteTrack multi-object tracking
- **[zones.py](src/zones.py)** - Zone management system
- **[rules.py](src/rules.py)** - Behavioral analysis engine

### Data Management
- **[evidence.py](src/evidence.py)** - Evidence capture & storage
- **[database.py](src/database.py)** - SQLite database operations ⭐ NEW
- **[video_source.py](src/video_source.py)** - Video source abstraction ⭐ NEW

### Communication
- **[alerts.py](src/alerts.py)** - Telegram notification system
- **[stream_manager.py](src/stream_manager.py)** - Live video streaming
- **[description_generator.py](src/description_generator.py)** - AI descriptions

### Utilities
- **[config_loader.py](src/config_loader.py)** - Configuration loader
- **[logging_config.py](src/logging_config.py)** - Logging setup
- **[activity_tracker.py](src/activity_tracker.py)** - Statistics tracker
- **[utils.py](src/utils.py)** - Helper functions
- **[zone_calibrator.py](src/zone_calibrator.py)** - Zone calibration tool

---

## 🎨 Web Interface (templates/)

- **[base.html](templates/base.html)** - Base template with navigation
- **[login.html](templates/login.html)** - Professional login page ⭐ NEW
- **[dashboard.html](templates/dashboard.html)** - Evidence gallery
- **[live.html](templates/live.html)** - Live video feed
- **[devices.html](templates/devices.html)** - Device management

---

## 🧪 Testing (tests/)

- **[test_rules.py](tests/test_rules.py)** - Behavioral rules unit tests

---

## 📊 Data Directories

### Evidence Storage
- **[evidence/](evidence/)** - Incident photos and metadata
  - `*.jpg` - Incident snapshots
  - `*.json` - Metadata (legacy mode)
  - `thumbnails/` - Auto-generated thumbnails
  - `json_backup/` - Backups after migration

### Application Data
- **[data/](data/)** - Application database ⭐ NEW
  - `autoguard.db` - SQLite database

### Logs
- **[logs/](logs/)** - Application logs
  - `autoguard_*.log` - Timestamped log files

### Cache
- **[stream_cache/](stream_cache/)** - Video stream cache (temporary)

---

## 🎓 Learning Path

### For New Users
1. ✅ [README.md](README.md) - Understand what AutoGuard does
2. ✅ [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Learn quick commands
3. ✅ [docs/guides/QUICKSTART_v1.1.md](docs/guides/QUICKSTART_v1.1.md) - Set up system
4. ✅ [docs/guides/TELEGRAM_QUICKSTART.md](docs/guides/TELEGRAM_QUICKSTART.md) - Enable alerts
5. ✅ Run: `python -m src.main`

### For Developers
1. ✅ [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Understand organization
2. ✅ [src/main.py](src/main.py) - Study detection engine
3. ✅ [src/rules.py](src/rules.py) - Review behavioral rules
4. ✅ [docs/API.md](docs/API.md) - Explore API endpoints
5. ✅ [docs/SECURITY.md](docs/SECURITY.md) - Security practices

### For System Admins
1. ✅ [docs/guides/DEPLOYMENT_GUIDE.md](docs/guides/DEPLOYMENT_GUIDE.md) - Deploy to production
2. ✅ [docker-compose.yml](docker-compose.yml) - Container deployment
3. ✅ [config/config.yaml](config/config.yaml) - System configuration
4. ✅ [docs/SECURITY.md](docs/SECURITY.md) - Security hardening

---

## 🔍 Find What You Need

### I want to...

**...start using AutoGuard**
→ [docs/guides/QUICKSTART_v1.1.md](docs/guides/QUICKSTART_v1.1.md)

**...set up Telegram alerts**
→ [docs/guides/TELEGRAM_QUICKSTART.md](docs/guides/TELEGRAM_QUICKSTART.md)

**...use an IP camera**
→ [docs/guides/RTSP_GUIDE.md](docs/guides/RTSP_GUIDE.md)

**...understand the code**
→ [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) → [src/](src/)

**...deploy to production**
→ [docs/guides/DEPLOYMENT_GUIDE.md](docs/guides/DEPLOYMENT_GUIDE.md)

**...migrate to database**
→ Run: `python tools/migrate_to_database.py`

**...find my camera**
→ Run: `python tools/discover_cameras.py`

**...troubleshoot Telegram**
→ [docs/guides/TELEGRAM_FIX.md](docs/guides/TELEGRAM_FIX.md)

**...see the roadmap**
→ [PROJECT_PROGRESS.md](PROJECT_PROGRESS.md)

**...contribute**
→ [GITHUB_PUSH_GUIDE.md](docs/guides/GITHUB_PUSH_GUIDE.md)

---

## 📱 Quick Links

| What | Where |
|------|-------|
| **GitHub** | https://github.com/dhruvkasar/autoguard |
| **Telegram Bot** | @Your_autoguard_Bot |
| **Dashboard** | http://localhost:5000 |
| **Documentation** | [docs/](docs/) |
| **Tools** | [tools/](tools/) |

---

## 🆘 Getting Help

### Troubleshooting
1. Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Common tasks
2. Run diagnostics: `python tools/check_telegram.py`
3. Check logs: `logs/autoguard_*.log`
4. See guides: [docs/guides/](docs/guides/)

### Support Resources
- **Documentation:** 18 comprehensive guides
- **Tools:** 9 diagnostic/setup scripts
- **GitHub Issues:** Report bugs/requests
- **Project Structure:** Detailed file organization

---

## ✨ What's New in v1.1.0

### Major Features
- ✅ **CSRF Protection** - Flask-WTF security
- ✅ **Database Integration** - SQLite with migration
- ✅ **RTSP Support** - IP camera compatibility
- ✅ **Professional Login** - Modern UI
- ✅ **Video Abstraction** - USB/RTSP/RTMP/HTTP/Files

### New Documentation
- [TELEGRAM_QUICKSTART.md](docs/guides/TELEGRAM_QUICKSTART.md)
- [RTSP_GUIDE.md](docs/guides/RTSP_GUIDE.md)
- [QUICKSTART_v1.1.md](docs/guides/QUICKSTART_v1.1.md)
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

### New Tools
- `tools/discover_cameras.py`
- `tools/check_telegram.py`
- `tools/diagnose_telegram.py`
- `tools/migrate_to_database.py`

---

## 📈 Project Stats

- **Total Files:** 53 documented files
- **Lines of Code:** ~15,450
- **Documentation:** 18 guides
- **Tools:** 9 utilities
- **Source Modules:** 17
- **Templates:** 5

---

## 🎯 Status

**Version:** 1.1.0  
**Release Date:** October 5, 2026  
**Status:** ✅ Production Ready  

**Components:**
- ✅ Detection Engine
- ✅ Web Dashboard (CSRF Protected)
- ✅ Telegram Alerts (Working)
- ✅ Database Storage (Available)
- ✅ RTSP Support (Ready)
- ✅ Documentation (Complete)
- ✅ Tools (9 utilities)

---

**AutoGuard v1.1.0 - Your Complete Security Solution**  
*Professional • Organized • Production-Ready* 🚀

---

**Navigation Tip:** Use Ctrl+F to search for specific topics in this file!
