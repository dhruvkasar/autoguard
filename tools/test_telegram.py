"""
Test Telegram Alert System
Verifies Telegram bot configuration and sends a test alert
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.alerts import TelegramAlerter
from src.logging_config import setup_logging

def print_banner():
    print("\n" + "="*60)
    print("AutoGuard - Telegram Alert Test")
    print("="*60 + "\n")

def main():
    print_banner()
    
    # Load environment variables
    load_dotenv()
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_ids_str = os.getenv('TELEGRAM_CHAT_IDS', '')
    camera_id = os.getenv('CAMERA_ID', 'TEST_CAM')
    
    # Validate configuration
    print("Checking configuration...\n")
    
    if not bot_token:
        print("ERROR: TELEGRAM_BOT_TOKEN not found in .env file")
        print("\nSteps to fix:")
        print("1. Create a bot with @BotFather on Telegram")
        print("2. Copy the bot token")
        print("3. Add to .env file:")
        print("   TELEGRAM_BOT_TOKEN=your_bot_token_here")
        print("\nSee TELEGRAM_SETUP.md for detailed instructions")
        return 1
    
    if not chat_ids_str:
        print("ERROR: TELEGRAM_CHAT_IDS not found in .env file")
        print("\nSteps to fix:")
        print("1. Search for @userinfobot on Telegram")
        print("2. Send a message to get your Chat ID")
        print("3. Add to .env file:")
        print("   TELEGRAM_CHAT_IDS=your_chat_id")
        print("\nSee TELEGRAM_SETUP.md for detailed instructions")
        return 1
    
    chat_ids = [cid.strip() for cid in chat_ids_str.split(',') if cid.strip()]
    
    print("Configuration found:")
    print(f"  Bot Token: {bot_token[:20]}...{bot_token[-10:]}")
    print(f"  Chat IDs: {', '.join(chat_ids)}")
    print(f"  Camera ID: {camera_id}")
    print()
    
    # Setup alerter
    print("Initializing Telegram alerter...\n")
    logger = setup_logging("logs")
    
    alerter = TelegramAlerter(
        enabled=True,
        token=bot_token,
        chat_ids=chat_ids,
        camera_id=camera_id,
        logger=logger
    )
    
    # Send test message (text only - no photo)
    print("Sending test alert...")
    print("-" * 60)
    
    # Create test caption
    caption = (
        f"🚨 AutoGuard Test Alert\n\n"
        f"Camera: {camera_id}\n"
        f"Rule: System Test\n"
        f"Person ID: 999\n"
        f"Time: {os.popen('echo %date% %time%').read().strip()}\n\n"
        f"Description:\n"
        f"This is a test alert from AutoGuard. If you see this message, "
        f"your Telegram integration is working correctly!"
    )
    
    # Try to send text message using Telegram API directly
    success = False
    try:
        import requests
        for chat_id in chat_ids:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": caption,
                "parse_mode": "HTML"
            }
            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                print(f"Test alert sent to chat ID: {chat_id}")
                success = True
            else:
                print(f"Failed to send to chat ID {chat_id}: {response.text}")
                logger.error(f"Telegram API error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error sending test alert: {e}")
        logger.error(f"Test alert error: {e}")
    
    print("-" * 60)
    print()
    
    if success:
        print("SUCCESS! Test alert sent successfully!")
        print("\nCheck your Telegram app - you should see the alert.")
        print("\nNext steps:")
        print("1. Start AutoGuard detection: python -m src.main")
        print("2. You'll receive real alerts when incidents are detected")
        print("   (Real alerts will include photos!)")
        print("\nTo adjust alert settings, edit config/config.yaml:")
        print("  alerts:")
        print("    cooldown_seconds: 15  # Time between alerts")
        print("    daily_cap: 50         # Max alerts per day")
        return 0
    else:
        print("FAILED to send test alert")
        print("\nTroubleshooting:")
        print("1. Check bot token is correct")
        print("2. Verify chat ID is correct")
        print("3. Make sure you started a chat with your bot (click START)")
        print("4. Check internet connection")
        print("5. Review logs/autoguard_*.log for details")
        print("\nSee TELEGRAM_SETUP.md for detailed troubleshooting")
        return 1

if __name__ == '__main__':
    sys.exit(main())
