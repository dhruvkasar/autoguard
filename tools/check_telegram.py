"""
Simple Telegram Checker - No Unicode Issues
"""
import os
from dotenv import load_dotenv
import requests

load_dotenv()

token = os.getenv('TELEGRAM_BOT_TOKEN', '').strip()
chat_id = os.getenv('TELEGRAM_CHAT_IDS', '').strip()

print("\n" + "="*60)
print("Telegram Configuration Check")
print("="*60 + "\n")

print(f"Bot Token: {token[:20]}...{token[-10:]}")
print(f"Chat ID: {chat_id}")
print()

# Test 1: Check bot token
print("Test 1: Checking bot token...")
try:
    r = requests.get(f'https://api.telegram.org/bot{token}/getMe', timeout=10)
    data = r.json()
    
    if data.get('ok'):
        bot_info = data.get('result', {})
        print(f"[OK] Bot is valid")
        print(f"     Name: {bot_info.get('first_name')}")
        print(f"     Username: @{bot_info.get('username')}")
        bot_username = bot_info.get('username')
    else:
        print(f"[FAIL] Invalid bot token")
        print(f"       Error: {data.get('description')}")
        exit(1)
except Exception as e:
    print(f"[FAIL] Connection error: {e}")
    exit(1)

print()

# Test 2: Check for messages
print("Test 2: Looking for messages from you...")
try:
    r = requests.get(f'https://api.telegram.org/bot{token}/getUpdates', timeout=10)
    data = r.json()
    
    if data.get('ok'):
        updates = data.get('result', [])
        print(f"[INFO] Found {len(updates)} message(s)")
        
        if updates:
            print("\nChats found:")
            for update in updates:
                if 'message' in update:
                    chat = update['message']['chat']
                    cid = chat['id']
                    name = f"{chat.get('first_name', '')} {chat.get('last_name', '')}".strip()
                    print(f"  - Name: {name}")
                    print(f"    Chat ID: {cid}")
            
            # Get the first chat ID
            first_chat = updates[0]['message']['chat']['id']
            
            # Test 3: Try sending message
            print(f"\nTest 3: Sending test message to chat {first_chat}...")
            r = requests.post(
                f'https://api.telegram.org/bot{token}/sendMessage',
                data={'chat_id': first_chat, 'text': 'Test message from AutoGuard!'},
                timeout=10
            )
            result = r.json()
            
            if result.get('ok'):
                print("[OK] Test message sent successfully!")
                print("\nCHECK YOUR TELEGRAM APP NOW!")
                print()
                print("="*60)
                print("SUCCESS - Configuration is correct!")
                print("="*60)
                print("\nAdd to .env file:")
                print(f"TELEGRAM_BOT_TOKEN={token}")
                print(f"TELEGRAM_CHAT_IDS={first_chat}")
                print()
            else:
                print(f"[FAIL] Could not send message")
                print(f"       Error: {result.get('description')}")
        else:
            print("\n[ACTION NEEDED]")
            print(f"No messages found. Please:")
            print(f"1. Open Telegram app")
            print(f"2. Search: @{bot_username}")
            print(f"3. Click START button")
            print(f"4. Send a message (e.g., 'hi')")
            print(f"5. Run this script again")
            print()
            print(f"Direct link: https://t.me/{bot_username}")
    else:
        print(f"[FAIL] Could not get updates")
        
except Exception as e:
    print(f"[FAIL] Error: {e}")

print()
