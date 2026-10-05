"""
Telegram Configuration Diagnostic Tool
Checks your bot token, chat ID, and connection
"""

import os
import sys
import requests
from dotenv import load_dotenv

def print_banner():
    print("\n" + "="*60)
    print("AutoGuard - Telegram Diagnostic Tool")
    print("="*60 + "\n")

def test_bot_token(token):
    """Test if bot token is valid"""
    print("Step 1: Testing Bot Token...")
    print("-" * 60)
    
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get('ok'):
            bot_info = data.get('result', {})
            print("✓ Bot token is VALID")
            print(f"  Bot Name: {bot_info.get('first_name', 'Unknown')}")
            print(f"  Bot Username: @{bot_info.get('username', 'Unknown')}")
            print(f"  Bot ID: {bot_info.get('id', 'Unknown')}")
            return True, bot_info.get('username')
        else:
            print("✗ Bot token is INVALID")
            print(f"  Error: {data.get('description', 'Unknown error')}")
            return False, None
    except Exception as e:
        print(f"✗ Connection error: {e}")
        return False, None

def get_updates(token):
    """Get recent messages to find chat ID"""
    print("\nStep 2: Checking for Messages...")
    print("-" * 60)
    
    try:
        url = f"https://api.telegram.org/bot{token}/getUpdates"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if not data.get('ok'):
            print("✗ Could not fetch updates")
            return []
        
        updates = data.get('result', [])
        
        if not updates:
            print("✗ No messages found yet")
            print("\n  ACTION REQUIRED:")
            print("  1. Open Telegram app")
            print("  2. Search for your bot")
            print("  3. Click START button")
            print("  4. Send a message (e.g., 'hello')")
            print("  5. Run this diagnostic again")
            return []
        
        print(f"✓ Found {len(updates)} message(s)")
        
        chat_ids = []
        for update in updates:
            if 'message' in update:
                chat = update['message']['chat']
                chat_id = chat['id']
                chat_type = chat['type']
                
                if chat_type == 'private':
                    name = f"{chat.get('first_name', '')} {chat.get('last_name', '')}".strip()
                    print(f"\n  Chat found:")
                    print(f"    Name: {name}")
                    print(f"    Chat ID: {chat_id}")
                    print(f"    Username: @{chat.get('username', 'N/A')}")
                    chat_ids.append(str(chat_id))
        
        return chat_ids
    except Exception as e:
        print(f"✗ Error fetching updates: {e}")
        return []

def test_send_message(token, chat_id):
    """Test sending a message"""
    print("\nStep 3: Testing Message Delivery...")
    print("-" * 60)
    
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": "✓ AutoGuard Telegram test successful!\n\nYour bot is configured correctly."
        }
        
        response = requests.post(url, data=data, timeout=10)
        result = response.json()
        
        if result.get('ok'):
            print("✓ Test message sent successfully!")
            print(f"  Message ID: {result.get('result', {}).get('message_id')}")
            print("\n  Check your Telegram app - you should see the test message!")
            return True
        else:
            print("✗ Failed to send message")
            print(f"  Error: {result.get('description', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"✗ Error sending message: {e}")
        return False

def main():
    print_banner()
    
    # Load .env file
    load_dotenv()
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '').strip()
    chat_ids_str = os.getenv('TELEGRAM_CHAT_IDS', '').strip()
    
    if not bot_token:
        print("ERROR: TELEGRAM_BOT_TOKEN not found in .env file")
        print("\nPlease add your bot token to .env:")
        print("  TELEGRAM_BOT_TOKEN=your_bot_token_here")
        return 1
    
    print(f"Bot Token: {bot_token[:20]}...{bot_token[-10:]}")
    if chat_ids_str:
        print(f"Chat ID from .env: {chat_ids_str}")
    print()
    
    # Test bot token
    token_valid, bot_username = test_bot_token(bot_token)
    if not token_valid:
        print("\n" + "="*60)
        print("DIAGNOSIS: Invalid Bot Token")
        print("="*60)
        print("\nFIX:")
        print("1. Go to @BotFather on Telegram")
        print("2. Send: /mybots")
        print("3. Select your bot")
        print("4. Click 'API Token'")
        print("5. Copy the token")
        print("6. Update TELEGRAM_BOT_TOKEN in .env")
        return 1
    
    # Get updates to find chat ID
    found_chat_ids = get_updates(bot_token)
    
    if not found_chat_ids:
        print("\n" + "="*60)
        print("DIAGNOSIS: No Messages Found")
        print("="*60)
        print("\nYour bot token is valid, but you need to start a chat:")
        print(f"\n1. Open Telegram")
        print(f"2. Search for: @{bot_username}")
        print(f"3. Click START button")
        print(f"4. Send any message (e.g., 'hi')")
        print(f"5. Run this diagnostic again")
        print(f"\nOr visit: https://t.me/{bot_username}")
        return 1
    
    # Compare with .env
    env_chat_ids = [cid.strip() for cid in chat_ids_str.split(',') if cid.strip()]
    
    if chat_ids_str and found_chat_ids:
        if set(env_chat_ids) == set(found_chat_ids):
            print("\n✓ Chat ID in .env matches Telegram")
        else:
            print(f"\n⚠ Chat ID mismatch!")
            print(f"  .env has: {', '.join(env_chat_ids)}")
            print(f"  Telegram has: {', '.join(found_chat_ids)}")
            print(f"\n  UPDATE .env with correct Chat ID:")
            print(f"  TELEGRAM_CHAT_IDS={','.join(found_chat_ids)}")
    
    # Test sending message
    test_chat_id = found_chat_ids[0]
    send_success = test_send_message(bot_token, test_chat_id)
    
    print("\n" + "="*60)
    print("DIAGNOSTIC SUMMARY")
    print("="*60)
    
    if token_valid and found_chat_ids and send_success:
        print("\n✓✓✓ ALL TESTS PASSED! ✓✓✓")
        print("\nYour Telegram integration is working correctly!")
        print(f"\nConfiguration for .env:")
        print(f"  TELEGRAM_BOT_TOKEN={bot_token}")
        print(f"  TELEGRAM_CHAT_IDS={','.join(found_chat_ids)}")
        print("\nNext steps:")
        print("  1. Make sure .env has correct values above")
        print("  2. Run: python -m src.main")
        print("  3. You'll receive alerts on your phone!")
        return 0
    else:
        print("\n✗ Some tests failed")
        print("\nPlease follow the instructions above to fix the issues")
        return 1

if __name__ == '__main__':
    sys.exit(main())
