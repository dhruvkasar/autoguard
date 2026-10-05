# 📱 Telegram Alert Setup - Quick Guide

**Time to Complete:** 10 minutes  
**Status:** ✅ Already Implemented in AutoGuard

---

## 🚀 Quick Setup (3 Steps)

### Step 1️⃣: Create Your Bot (3 minutes)

1. Open **Telegram** on your phone
2. Search for: `@BotFather`
3. Send command: `/newbot`
4. Choose a name: `AutoGuard Alert Bot`
5. Choose username: `your_autoguard_bot`
6. **Copy the token** BotFather sends you

**Example Token:**
```
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz1234567890
```

---

### Step 2️⃣: Get Your Chat ID (2 minutes)

1. Search for: `@userinfobot`
2. Start chat and send any message
3. Bot replies with your info
4. **Copy the "Id" number** (e.g., `123456789`)

---

### Step 3️⃣: Configure AutoGuard (3 minutes)

Edit `D:\Major Project\.env`:

```bash
# Add these lines:
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz1234567890
TELEGRAM_CHAT_IDS=123456789
CAMERA_ID=ENTRANCE_CAM
```

**Save the file!**

---

## ✅ Test Your Setup

```bash
# Run test script
python test_telegram.py
```

**Expected Result:**
```
SUCCESS! Test alert sent successfully!

Check your Telegram app - you should see the alert.
```

---

## 📱 What You'll Receive

When AutoGuard detects an incident:

```
🚨 AutoGuard Security Alert

Camera: ENTRANCE_CAM
Rule: Loitering Detected
Person ID: 42
Time: 2026-09-26 13:15:32

Description:
Person #42 has been loitering in the shelf 
area for 8 seconds, exceeding the 5-second 
threshold.
```

**Plus a photo attached!** 📸

---

## 🎛️ Configuration Options

### Adjust Alert Frequency

Edit `config/config.yaml`:

```yaml
alerts:
  enabled: true
  cooldown_seconds: 15    # Wait 15s between same alerts
  daily_cap: 50          # Max 50 alerts per day
```

### Multiple Recipients

Edit `.env`:

```bash
# Send to multiple phones
TELEGRAM_CHAT_IDS=123456789,987654321,555666777
```

---

## 🔧 Troubleshooting

### Problem: No test alert received

**Solution:**
1. Make sure you **started** a chat with your bot (click START button)
2. Check bot token is correct (no spaces)
3. Check chat ID is correct
4. Verify internet connection

### Problem: "Invalid bot token"

**Solution:**
1. Go back to @BotFather
2. Send `/token` to get your bot list
3. Copy the correct token
4. Update `.env` file

### Problem: Can't find chat ID

**Use our helper script:**
```bash
python get_telegram_chat_id.py YOUR_BOT_TOKEN
```

---

## 📋 Complete Setup Checklist

- [ ] Created bot with @BotFather
- [ ] Got bot token
- [ ] Got chat ID from @userinfobot
- [ ] Added token to .env file
- [ ] Added chat ID to .env file
- [ ] Started chat with bot (clicked START)
- [ ] Ran test: `python test_telegram.py`
- [ ] Received test alert on phone
- [ ] Ready to run AutoGuard!

---

## 🚀 Run AutoGuard with Alerts

```bash
# Start detection (Terminal 1)
python -m src.main

# You'll now receive alerts on your phone!
```

---

## 📖 Need More Help?

See **TELEGRAM_SETUP.md** for:
- Detailed instructions
- Advanced configuration
- Group chat setup
- Multiple camera setup
- Troubleshooting guide

---

## 🎯 Quick Commands Reference

```bash
# Test Telegram alerts
python test_telegram.py

# Get your chat ID
python get_telegram_chat_id.py YOUR_BOT_TOKEN

# Start detection with alerts
python -m src.main

# Start web dashboard
python -m src.server
```

---

## ✨ Features

- 📸 **Instant photo alerts** - See the incident immediately
- 🤖 **AI descriptions** - Natural language incident reports
- ⏱️ **Configurable cooldown** - Prevent alert spam
- 📊 **Metadata included** - Person ID, timestamp, camera, rule
- 👥 **Multiple recipients** - Alert your whole team
- 🔕 **Daily cap** - Prevent alert fatigue
- 🌍 **Works anywhere** - As long as you have internet

---

**Current Time:** September 26, 2026 at 1:18 PM  
**Your System:** AutoGuard v1.1.0  
**Telegram Integration:** ✅ Ready to Configure

Get real-time security alerts on your phone in just 10 minutes! 📱🚨
