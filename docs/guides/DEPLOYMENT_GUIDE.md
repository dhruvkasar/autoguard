# AutoGuard Deployment Guide
**How to Share This Prototype with Your Friend's Laptop**

Created: August 28, 2026 (for tomorrow's demo)

---

## 🎯 Quick Overview

You have **3 options** to share this prototype:
1. **USB Transfer** (Recommended - Fastest for demo)
2. **Network Share** (Good for local network)
3. **Git Repository** (Best for long-term, but requires setup)

---

## Option 1: USB Transfer (RECOMMENDED FOR DEMO)

### 📦 FOR YOU (Sender)

#### Step 1: Create Transfer Package

**1A. Create a clean copy folder**
```powershell
# Create deployment folder on Desktop
New-Item -ItemType Directory -Path "$env:USERPROFILE\Desktop\AutoGuard_Transfer" -Force
```

**1B. Copy essential files (excluding large folders)**
```powershell
# Navigate to your project
cd "D:\Major Project"

# Copy files to transfer folder
$dest = "$env:USERPROFILE\Desktop\AutoGuard_Transfer"

# Copy source code
Copy-Item -Path "src" -Destination $dest -Recurse -Force

# Copy config
Copy-Item -Path "config" -Destination $dest -Recurse -Force

# Copy templates and static
Copy-Item -Path "templates" -Destination $dest -Recurse -Force
Copy-Item -Path "static" -Destination $dest -Recurse -Force

# Copy tests
Copy-Item -Path "tests" -Destination $dest -Recurse -Force

# Copy essential files
Copy-Item -Path "requirements.txt" -Destination $dest -Force
Copy-Item -Path "Dockerfile" -Destination $dest -Force
Copy-Item -Path "docker-compose.yml" -Destination $dest -Force
Copy-Item -Path ".env.example" -Destination $dest -Force
Copy-Item -Path "README.md" -Destination $dest -Force
Copy-Item -Path "QUICKSTART.md" -Destination $dest -Force
Copy-Item -Path "DEMO_GUIDE.md" -Destination $dest -Force
Copy-Item -Path "SECURITY_FIXES.md" -Destination $dest -Force
Copy-Item -Path "CODEBASE_HEALTH_REPORT.md" -Destination $dest -Force

# Copy batch files
Copy-Item -Path "*.bat" -Destination $dest -Force

# Copy Python scripts in root
Copy-Item -Path "test_camera.py" -Destination $dest -Force
Copy-Item -Path "test_stream.py" -Destination $dest -Force

# Create empty directories
New-Item -ItemType Directory -Path "$dest\logs" -Force
New-Item -ItemType Directory -Path "$dest\evidence" -Force
New-Item -ItemType Directory -Path "$dest\stream_cache" -Force

# Copy YOLO weights if exists
if (Test-Path "yolov8n.pt") {
    Copy-Item -Path "yolov8n.pt" -Destination $dest -Force
}

Write-Output "✅ Transfer package created at: $dest"
```

**1C. Create your .env file for transfer**
```powershell
# Create .env file with your tokens (copy from your existing .env)
Copy-Item -Path ".env" -Destination "$dest\.env" -Force
```

**⚠️ IMPORTANT:** Check that .env has strong tokens set!

**1D. Check package size**
```powershell
$dest = "$env:USERPROFILE\Desktop\AutoGuard_Transfer"
$size = (Get-ChildItem -Path $dest -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Output "Package size: $([math]::Round($size, 2)) MB"
```

Should be around **10-15 MB** (without .venv)

**1E. Compress to ZIP (Optional but recommended)**
```powershell
$dest = "$env:USERPROFILE\Desktop\AutoGuard_Transfer"
$zipPath = "$env:USERPROFILE\Desktop\AutoGuard_Transfer.zip"

# Compress
Compress-Archive -Path "$dest\*" -DestinationPath $zipPath -Force

Write-Output "✅ ZIP created at: $zipPath"
Write-Output "Size: $([math]::Round((Get-Item $zipPath).Length / 1MB, 2)) MB"
```

**1F. Copy to USB drive**
```powershell
# Find your USB drive letter (e.g., E:, F:, G:)
Get-PSDrive -PSProvider FileSystem

# Copy ZIP to USB (replace E: with your drive letter)
Copy-Item -Path "$env:USERPROFILE\Desktop\AutoGuard_Transfer.zip" -Destination "E:\AutoGuard_Transfer.zip"

Write-Output "✅ Copied to USB drive"
```

---

### 📥 FOR YOUR FRIEND (Receiver)

#### Step 2: Install Prerequisites

**2A. Check Python installation**
```powershell
# Open PowerShell as Administrator
python --version
# Should show Python 3.10 or 3.11
```

**If Python not installed:**
1. Download Python 3.11 from https://www.python.org/downloads/
2. Run installer
3. ✅ **CHECK** "Add Python to PATH"
4. Click "Install Now"
5. Restart PowerShell

**2B. Install Git (Optional, for future)**
Download from: https://git-scm.com/download/win

#### Step 3: Extract and Setup Project

**3A. Copy from USB to laptop**
```powershell
# Create project directory
New-Item -ItemType Directory -Path "D:\AutoGuard" -Force

# Copy from USB (replace E: with USB drive letter)
Copy-Item -Path "E:\AutoGuard_Transfer.zip" -Destination "D:\AutoGuard_Transfer.zip"

# Extract
Expand-Archive -Path "D:\AutoGuard_Transfer.zip" -DestinationPath "D:\AutoGuard" -Force

# Navigate to project
cd D:\AutoGuard
```

**3B. Create virtual environment**
```powershell
# Create virtual environment
python -m venv .venv

# Activate it
.\.venv\Scripts\Activate.ps1
```

**⚠️ If you get execution policy error:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**3C. Install dependencies**
```powershell
# Upgrade pip first
python -m pip install --upgrade pip

# Install requirements (this will take 5-10 minutes)
pip install -r requirements.txt

# Verify installation
pip list
```

**3D. Download YOLO weights (if not included)**
```powershell
# If yolov8n.pt is missing, download it
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

#### Step 4: Configure for Friend's System

**4A. Check camera index**
```powershell
# Test camera
python test_camera.py
```

Note the working camera index (usually 0 or 1)

**4B. Update config (if needed)**
```powershell
# Edit config\config.yaml
# Change video.source to the working camera index
notepad config\config.yaml
```

Look for:
```yaml
video:
  source: 0  # Change to 1 if camera 0 doesn't work
```

**4C. Verify .env file**
```powershell
# Check .env exists
Get-Content .env
```

Should show tokens (don't share these publicly!)

#### Step 5: Run the Application

**5A. Test basic detection**
```powershell
# Activate virtual environment if not already
.\.venv\Scripts\Activate.ps1

# Run detection
python src/main.py --source 0
```

Press 'q' to quit

**5B. Start web dashboard**
```powershell
# Open new PowerShell window in project folder
cd D:\AutoGuard
.\.venv\Scripts\Activate.ps1

# Start Flask server
python -m flask --app src.server run --host 127.0.0.1 --port 5000
```

**Or use the batch file:**
```powershell
.\start_dashboard.bat
```

**5C. Access dashboard**
Open browser: http://localhost:5000

Login with token from .env file (ADMIN_TOKEN, SECURITY_TOKEN, or VIEWER_TOKEN)

---

## Option 2: Network Share (Local Network Only)

### FOR YOU (Sender)

**1. Enable network sharing**
```powershell
# Share the project folder
# Right-click on "D:\Major Project" 
# → Properties → Sharing → Advanced Sharing
# → Check "Share this folder" → Permissions → Add "Everyone" Read access
```

**2. Find your IP address**
```powershell
ipconfig | Select-String "IPv4"
# Note your IP (e.g., 192.168.1.100)
```

### FOR YOUR FRIEND (Receiver)

**1. Connect to share**
```powershell
# In File Explorer address bar (replace IP with yours)
\\192.168.1.100\Major Project

# Copy entire folder to local drive
Copy-Item -Path "\\192.168.1.100\Major Project" -Destination "D:\AutoGuard" -Recurse
```

Then follow **Step 3B-5C** from USB method above.

---

## Option 3: Git Repository (For Long-term Sharing)

### Setup Git Repository

**FOR YOU (One-time setup):**

```powershell
cd "D:\Major Project"

# Initialize git
git init

# Add gitignore
# (Already created by the assistant)

# Add files
git add .

# Commit
git commit -m "Initial commit - AutoGuard MVP with security fixes"

# Option A: Push to GitHub (if you have account)
# Create repo on github.com first, then:
git remote add origin https://github.com/yourusername/autoguard.git
git branch -M main
git push -u origin main

# Option B: Push to GitLab
# Create repo on gitlab.com first, then:
git remote add origin https://gitlab.com/yourusername/autoguard.git
git branch -M main
git push -u origin main
```

**FOR YOUR FRIEND:**

```powershell
# Clone repository
cd D:\
git clone https://github.com/yourusername/autoguard.git
cd autoguard

# Follow steps 3B-5C from USB method
```

---

## 🔧 Troubleshooting Guide

### Common Issues

**1. "pip is not recognized"**
```powershell
# Reinstall Python and check "Add to PATH"
# Or use full path:
python -m pip install -r requirements.txt
```

**2. "No module named 'cv2'"**
```powershell
# Ensure virtual environment is activated
.\.venv\Scripts\Activate.ps1

# Reinstall opencv
pip install opencv-python --force-reinstall
```

**3. "Camera not opening"**
```powershell
# Try different camera indices
python src/main.py --source 0
python src/main.py --source 1
python src/main.py --source 2

# Check if other apps are using camera (Zoom, Teams, etc.)
```

**4. "Cannot activate virtual environment"**
```powershell
# Fix execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try again
.\.venv\Scripts\Activate.ps1
```

**5. "Import error: No module named 'src'"**
```powershell
# Make sure you're in project root directory
cd D:\AutoGuard

# Check __init__.py exists in src folder
Test-Path src\__init__.py
```

**6. "HTTPS redirect error when logging in"**
```powershell
# Edit src\server.py line 125
# Remove secure=True parameter temporarily:
# resp.set_cookie('auth_token', token, httponly=True, samesite='Strict', max_age=43200)
```

**7. "Port 5000 already in use"**
```powershell
# Use different port
python -m flask --app src.server run --host 127.0.0.1 --port 5001

# Or find and kill process using port 5000
netstat -ano | findstr :5000
taskkill /PID <process_id> /F
```

---

## 📋 Quick Setup Checklist (For Friend)

Print this checklist for your friend:

### Before Demo Day
- [ ] Python 3.10+ installed with PATH enabled
- [ ] Received AutoGuard_Transfer.zip from friend
- [ ] Extracted to D:\AutoGuard
- [ ] Virtual environment created (`.venv`)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] YOLO weights downloaded (`yolov8n.pt` exists)
- [ ] Camera tested (`python test_camera.py`)
- [ ] .env file has tokens set

### On Demo Day
- [ ] Virtual environment activated
- [ ] Detection tested: `python src/main.py --source 0`
- [ ] Dashboard tested: http://localhost:5000
- [ ] Can login with tokens from .env
- [ ] Evidence appears in dashboard
- [ ] Live feed working

---

## 🚀 Final Test Script

**Use this to verify everything works on friend's laptop:**

```powershell
# Test Script - Run on friend's laptop
cd D:\AutoGuard

Write-Output "1. Checking Python..."
python --version

Write-Output "`n2. Activating virtual environment..."
.\.venv\Scripts\Activate.ps1

Write-Output "`n3. Checking dependencies..."
python -c "import cv2, ultralytics, flask; print('✅ All imports successful')"

Write-Output "`n4. Checking YOLO weights..."
if (Test-Path "yolov8n.pt") { Write-Output "✅ YOLO weights found" } else { Write-Output "❌ YOLO weights missing" }

Write-Output "`n5. Checking .env..."
if (Test-Path ".env") { Write-Output "✅ .env found" } else { Write-Output "❌ .env missing" }

Write-Output "`n6. Checking config..."
if (Test-Path "config\config.yaml") { Write-Output "✅ Config found" } else { Write-Output "❌ Config missing" }

Write-Output "`n7. Running unit tests..."
python -m unittest discover tests

Write-Output "`n✅ Setup verification complete!"
Write-Output "`nReady to demo! Run: python src/main.py --source 0"
```

---

## 📞 Support Contact

If your friend faces issues during setup:
- Share this guide: `DEPLOYMENT_GUIDE.md`
- Check health report: `CODEBASE_HEALTH_REPORT.md`
- Review security fixes: `SECURITY_FIXES.md`
- Demo instructions: `DEMO_GUIDE.md`

---

## ⏱️ Time Estimates

| Task | Time Required |
|------|---------------|
| Creating transfer package | 5 minutes |
| USB transfer | 2 minutes |
| Installing Python (if needed) | 10 minutes |
| Extracting files | 1 minute |
| Creating virtual environment | 2 minutes |
| Installing dependencies | 5-10 minutes |
| Configuration & testing | 5 minutes |
| **TOTAL** | **30-40 minutes** |

**Recommendation:** Do this setup at least 2-3 hours before the demo to handle any unexpected issues!

---

## 💡 Pro Tips

1. **Test on friend's laptop BEFORE demo day**
2. **Keep a backup USB** with the zip file
3. **Screenshot the working dashboard** as backup
4. **Have mobile hotspot ready** if internet needed
5. **Charge both laptops fully** before demo
6. **Close unnecessary apps** during demo (Teams, Zoom, etc.)
7. **Test camera access** first thing on demo day

---

Good luck with your demo tomorrow! 🎉
