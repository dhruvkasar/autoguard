# AutoGuard - Telegram Alert System Setup Guide

**Status:** ✅ Fully Implemented (v1.0.0)  
**Last Updated:** September 26, 2026

---

## Overview

AutoGuard includes a complete Telegram notification system that sends:
- 📸 Real-time incident photos
- 🚨 Alert descriptions (AI-generated)
- 📊 Incident metadata (person ID, rule triggered, timestamp)
- 📱 Instant mobile push notifications

---

## Step-by-Step Setup (10 minutes)

### Step 1: Create a Telegram Bot

1. **Open Telegram on your phone**
   - Download from: https://telegram.org/ (if not installed)

2. **Search for "BotFather"**
   - Open Telegram
   - In search bar, type: `@BotFather`
   - Start a chat with BotFather (official Telegram bot)

3. **Create your bot**
   - Send command: `/newbot`
   - BotFather will ask for a name
   - Choose a name: `AutoGuard Alert Bot` (or any name you like)
   - Choose a username: `your_autoguard_bot` (must end with 'bot')

4. **Get your Bot Token**
   - BotFather will reply with a message like:
   ```
   Done! Congratulations on your new bot.
   You will find it at t.me/your_autoguard_bot
   
   Use this token to access the HTTP API:
   1234567890:ABCdefGHIjklMNOpqrsTUVwxyz1234567890
   
   Keep your token secure and store it safely...
   ```
   - **Copy this token** - you'll need it!

---

### Step 2: Get Your Chat ID

**Method 1: Using a Helper Bot (Easiest)**

1. **Search for "userinfobot"**
   - In Telegram search: `@userinfobot`
   - Start a chat with it

2. **Send any message**
   - Type anything (e.g., "hi")
   - The bot will reply with your user info

3. **Copy your Chat ID**
   - Look for the line: `Id: 123456789`
   - Copy this number (your Chat ID)

**Method 2: Using Your Bot (Alternative)**

1. **Start a chat with your new bot**
   - Find your bot: `@your_autoguard_bot`
   - Click "START" or send any message

2. **Use this Python script:**
   ```bash
   python get_telegram_chat_id.py YOUR_BOT_TOKEN
   ```
   (Script provided below)

---

### Step 3: Configure AutoGuard

1. **Edit your .env file**
   
   Open `D:\Major Project\.env` and add:
   
   ```bash
   # Telegram Bot Configuration
   TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz1234567890
   TELEGRAM_CHAT_IDS=123456789
   
   # Camera ID (appears in alerts)
   CAMERA_ID=ENTRANCE_CAM
   ```

2. **For multiple recipients:**
   ```bash
   # Send alerts to multiple people
   TELEGRAM_CHAT_IDS=123456789,987654321,555666777
   ```

3. **Verify in config.yaml** (optional tuning)
   
   Open `config/config.yaml`:
   
   ```yaml
   alerts:
     enabled: true
     cooldown_seconds: 15    # Minimum time between alerts
     daily_cap: 50           # Maximum alerts per day
   ```

---

### Step 4: Test the System

**Quick Test Script:**

Create `test_telegram.py`:

```python
"""Test Telegram alert system"""
import os
from dotenv import load_dotenv
from src.alerts import TelegramAlerter
from src.logging_config import setup_logging

# Load environment variables
load_dotenv()

# Setup
logger = setup_logging("logs")
alerter = TelegramAlerter(
    enabled=True,
    token=os.getenv('TELEGRAM_BOT_TOKEN'),
    chat_ids=os.getenv('TELEGRAM_CHAT_IDS', '').split(','),
    camera_id=os.getenv('CAMERA_ID', 'TEST_CAM'),
    logger=logger
)

# Send test alert
print("Sending test alert...")
success = alerter.send_alert(
    rule_name="Test Alert",
    person_id=999,
    description="This is a test alert from AutoGuard. If you see this, your Telegram integration is working!",
    image_path=None  # No image for test
)

if success:
    print("✅ Test alert sent successfully!")
    print("Check your Telegram app for the message.")
else:
    print("❌ Failed to send test alert.")
    print("Check your bot token and chat ID.")
```

**Run the test:**
```bash
python test_telegram.py
```

You should receive a message on your phone! 📱

---

## Configuration Options

### Alert Settings (config.yaml)

```yaml
alerts:
  enabled: true               # Enable/disable alerts
  cooldown_seconds: 15        # Minimum time between same alerts
  daily_cap: 50              # Max alerts per day (0 = unlimited)
  
  # These come from .env file:
  # token: from TELEGRAM_BOT_TOKEN
  # chat_ids: from TELEGRAM_CHAT_IDS
  # camera_id: from CAMERA_ID
```

### Cooldown Explained

**Prevents alert spam:**
- If "Loitering" is detected, wait 15 seconds before sending another loitering alert
- Different rule types have independent cooldowns
- Prevents hundreds of alerts for one incident

**Adjust cooldown:**
```yaml
alerts:
  cooldown_seconds: 30  # More relaxed (30 seconds)
  # or
  cooldown_seconds: 5   # More sensitive (5 seconds)
```

### Daily Cap Explained

**Prevents alert fatigue:**
- Limits total alerts sent per day
- Resets at midnight
- Set to 0 for unlimited

**Adjust cap:**
```yaml
alerts:
  daily_cap: 100  # Allow more alerts
  # or
  daily_cap: 0    # Unlimited
```

---

## Alert Message Format

When an incident is detected, you'll receive:

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

[Photo attached]
```

---

## Troubleshooting

### "Failed to send alert"

**1. Check Bot Token**
```bash
# Test your bot token
curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe
```

Should return bot info. If error, token is invalid.

**2. Check Chat ID**
- Make sure you started a chat with your bot (click START)
- Chat ID should be a number (positive or negative)
- No spaces or special characters

**3. Bot Permissions**
- Ensure bot has permission to send messages
- Check bot is not blocked

### "Bot not receiving messages"

**Start a conversation:**
1. Search for your bot in Telegram
2. Click START button
3. Send a message

### "Wrong Chat ID"

**Get correct Chat ID:**
```bash
# Use userinfobot
# Or run:
python get_telegram_chat_id.py YOUR_BOT_TOKEN
```

### "No alerts received"

**Check if alerts are enabled:**
```yaml
# config/config.yaml
alerts:
  enabled: true  # Make sure this is true
```

**Check detection is working:**
- Are incidents being detected?
- Check evidence folder for .jpg files
- Check logs for "Evidence captured" messages

**Check cooldown:**
- Maybe cooldown is preventing alerts
- Try reducing `cooldown_seconds`

---

## Advanced Configuration

### Multiple Cameras (Manual Setup)

**Camera 1 - Entrance:**
```bash
# .env
CAMERA_ID=ENTRANCE
TELEGRAM_CHAT_IDS=123456789
```

**Camera 2 - Checkout:**
```bash
# .env
CAMERA_ID=CHECKOUT
TELEGRAM_CHAT_IDS=987654321
```

### Group Chats

**Send alerts to a group:**

1. Create a Telegram group
2. Add your bot to the group
3. Get group chat ID (will be negative, e.g., `-987654321`)
4. Use group ID in .env:
   ```bash
   TELEGRAM_CHAT_IDS=-987654321
   ```

### Disable Alerts Temporarily

**Option 1: In config.yaml**
```yaml
alerts:
  enabled: false  # Disable all alerts
```

**Option 2: Remove from .env**
```bash
# Comment out or remove:
# TELEGRAM_BOT_TOKEN=...
# TELEGRAM_CHAT_IDS=...
```

---

## Helper Script: Get Chat ID

Create `get_telegram_chat_id.py`:

```python
"""
Get your Telegram Chat ID
Usage: python get_telegram_chat_id.py YOUR_BOT_TOKEN
"""

import sys
import requests

if len(sys.argv) < 2:
    print("Usage: python get_telegram_chat_id.py YOUR_BOT_TOKEN")
    print("\nExample:")
    print("python get_telegram_chat_id.py 1234567890:ABCdefGHI...")
    sys.exit(1)

bot_token = sys.argv[1]
url = f"https://api.telegram.org/bot{bot_token}/getUpdates"

print(f"\nFetching updates from Telegram bot...\n")

try:
    response = requests.get(url)
    data = response.json()
    
    if not data.get('ok'):
        print("❌ Error: Invalid bot token or API error")
        print(f"Response: {data}")
        sys.exit(1)
    
    updates = data.get('result', [])
    
    if not updates:
        print("❌ No messages found!")
        print("\nSteps:")
        print("1. Open Telegram")
        print("2. Search for your bot")
        print("3. Click START or send any message")
        print("4. Run this script again")
        sys.exit(1)
    
    print("✅ Found chat IDs:\n")
    
    chat_ids = set()
    for update in updates:
        if 'message' in update:
            chat = update['message']['chat']
            chat_id = chat['id']
            chat_type = chat['type']
            
            if chat_type == 'private':
                name = f"{chat.get('first_name', '')} {chat.get('last_name', '')}".strip()
                print(f"User: {name}")
                print(f"Chat ID: {chat_id}")
                print(f"Username: @{chat.get('username', 'N/A')}")
                print()
            else:
                title = chat.get('title', 'Unknown Group')
                print(f"Group: {title}")
                print(f"Chat ID: {chat_id}")
                print()
            
            chat_ids.add(chat_id)
    
    print("-" * 60)
    print("\nAdd to your .env file:")
    print("-" * 60)
    print(f"TELEGRAM_BOT_TOKEN={bot_token}")
    print(f"TELEGRAM_CHAT_IDS={','.join(map(str, chat_ids))}")
    print()

except Exception as e:
    print(f"❌ Error: {e}")
    print("\nMake sure:")
    print("1. Bot token is correct")
    print("2. You have internet connection")
    print("3. You sent a message to your bot")
```

**Usage:**
```bash
python get_telegram_chat_id.py 1234567890:ABCdefGHI...
```

---

## Security Best Practices

### 1. Keep Bot Token Secret
```bash
# ✅ GOOD - In .env file (not committed to git)
TELEGRAM_BOT_TOKEN=your_token_here

# ❌ BAD - Hardcoded in code
token = "1234567890:ABCdefGHI..."  # Don't do this!
```

### 2. Restrict Bot Permissions
- Bot should only need to send messages
- Don't make bot an admin unless necessary

### 3. Use Group Privacy Mode
- In group settings, enable privacy mode
- Bot only sees messages directed at it

### 4. Limit Chat IDs
- Only add trusted phone numbers
- Review TELEGRAM_CHAT_IDS periodically

---

## Example: Complete Setup

### Your .env file:
```bash
# Telegram Configuration
TELEGRAM_BOT_TOKEN=5678901234:XYZabcDEFghiJKLmnoPQRstuVWXyz123456
TELEGRAM_CHAT_IDS=123456789
CAMERA_ID=STORE_ENTRANCE

# Flask & Database
FLASK_SECRET_KEY=1038ec04186235219b5efdf1b6a989d2542f35f2f27b16689a357beda4049e33
USE_DATABASE=false

# Auth Tokens
ADMIN_TOKEN=admin123
SECURITY_TOKEN=security456
VIEWER_TOKEN=viewer789
```

### Your config.yaml:
```yaml
alerts:
  enabled: true
  cooldown_seconds: 15
  daily_cap: 50
```

### Start AutoGuard:
```bash
python -m src.main
```

**You'll now receive alerts on your phone!** 📱🚨

---

## Testing Checklist

- [ ] Bot created in BotFather
- [ ] Bot token copied to .env
- [ ] Chat ID obtained (using userinfobot)
- [ ] Chat ID added to .env
- [ ] Started chat with bot (clicked START)
- [ ] Test script run successfully
- [ ] Test alert received on phone
- [ ] AutoGuard detection running
- [ ] Real alert received during detection

---

## FAQ

**Q: Can I use multiple bots?**  
A: One bot is recommended, but you can use multiple by changing the token.

**Q: How fast are alerts?**  
A: Usually instant (< 1 second). Depends on internet connection.

**Q: Do I need Telegram Premium?**  
A: No, free Telegram account works perfectly.

**Q: Can I customize alert messages?**  
A: Yes, edit `src/alerts.py` and modify the message format.

**Q: Will this use my phone data?**  
A: Minimal data usage. Photos are typically 50-200 KB each.

**Q: Can I turn off photo attachments?**  
A: Yes, modify `src/alerts.py` to skip `send_photo()` call.

**Q: What if my phone is off?**  
A: Telegram stores messages. You'll receive them when you turn on your phone.

**Q: Can I receive alerts on desktop?**  
A: Yes! Telegram has desktop apps for Windows/Mac/Linux.

---

## Next Steps

After setting up Telegram:

1. ✅ Configure bot and chat ID
2. ✅ Test with test script
3. ✅ Run AutoGuard detection
4. ✅ Verify alerts are received
5. ✅ Adjust cooldown/cap as needed
6. ✅ Add additional recipients if needed

---

## Support

**Issues with Telegram setup?**

1. Check logs: `logs/autoguard_*.log`
2. Look for "Telegram" or "alert" messages
3. Run test script: `python test_telegram.py`
4. Verify bot token with BotFather
5. Check internet connection

**Still having issues?**

See main README.md or check the GitHub issues page.

---

**Telegram Integration:** ✅ Fully Implemented & Ready  
**Setup Time:** ~10 minutes  
**Difficulty:** Easy  

Enjoy real-time security alerts on your phone! 📱🚨
