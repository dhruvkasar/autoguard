"""
Get Your Telegram Chat ID
Helper script to retrieve your Telegram chat ID for AutoGuard alerts

Usage: python get_telegram_chat_id.py YOUR_BOT_TOKEN
"""

import sys
import requests

def print_banner():
    print("\n" + "="*60)
    print("AutoGuard - Telegram Chat ID Finder")
    print("="*60 + "\n")

def main():
    print_banner()
    
    if len(sys.argv) < 2:
        print("Usage: python get_telegram_chat_id.py YOUR_BOT_TOKEN")
        print("\nExample:")
        print("python get_telegram_chat_id.py 1234567890:ABCdefGHI...")
        print("\nTo get a bot token:")
        print("1. Open Telegram")
        print("2. Search for @BotFather")
        print("3. Send /newbot and follow instructions")
        print("4. Copy the token BotFather gives you")
        print("\nSee TELEGRAM_SETUP.md for detailed instructions")
        sys.exit(1)
    
    bot_token = sys.argv[1]
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    
    print(f"Fetching updates from Telegram bot...\n")
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if not data.get('ok'):
            print("ERROR: Invalid bot token or API error")
            print(f"Response: {data.get('description', 'Unknown error')}")
            print("\nMake sure:")
            print("1. Bot token is correct (copy from BotFather)")
            print("2. Token has no extra spaces")
            print("3. You have internet connection")
            sys.exit(1)
        
        updates = data.get('result', [])
        
        if not updates:
            print("No messages found!")
            print("\nBefore running this script:")
            print("1. Open Telegram app")
            print("2. Search for your bot")
            print("3. Click START button")
            print("4. Send any message (e.g., 'hi')")
            print("5. Run this script again")
            sys.exit(1)
        
        print("Found chat IDs:\n")
        
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
                    username = chat.get('username', '')
                    if username:
                        print(f"Username: @{username}")
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
        
        print("Next steps:")
        print("1. Copy the lines above")
        print("2. Open .env file in your project")
        print("3. Paste the configuration")
        print("4. Save the file")
        print("5. Run: python test_telegram.py")
        print()

    except requests.exceptions.Timeout:
        print("ERROR: Request timeout")
        print("Check your internet connection and try again")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Network error: {e}")
        print("\nMake sure:")
        print("1. You have internet connection")
        print("2. No firewall is blocking Telegram API")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
