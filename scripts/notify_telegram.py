import os
import sys
import json
import urllib.request
import urllib.parse
from pathlib import Path

def get_env_var(var_name):
    # 1. Try environment variables first
    val = os.environ.get(var_name)
    if val:
        return val
    
    # 2. Try parsing .env file in the current working directory
    env_path = Path('.env')
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        k, v = line.split('=', 1)
                        if k.strip() == var_name:
                            return v.strip().strip('"').strip("'")
    return None

def send_message(message):
    token = get_env_var('TELEGRAM_BOT_TOKEN')
    chat_id = get_env_var('TELEGRAM_CHAT_ID')

    if not token or not chat_id:
        print("Skipping Telegram Notification.", file=sys.stderr)
        print("Reason: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is missing in .env or environment.", file=sys.stderr)
        print(f"Message that would have been sent:\n{message}", file=sys.stderr)
        # We exit with 0 so we don't break the agent's workflow if they haven't configured it yet.
        sys.exit(0)

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = json.dumps({
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }).encode('utf-8')
    
    headers = {
        "Content-Type": "application/json"
    }

    try:
        req = urllib.request.Request(url, data=data, headers=headers)
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                print("Telegram notification sent successfully.")
            else:
                print(f"Warning: Unexpected response status: {response.status}", file=sys.stderr)
    except Exception as e:
        print(f"Error sending Telegram notification: {e}", file=sys.stderr)
        sys.exit(0) # Do not break workflow

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python scripts/notify_telegram.py \"Your message here\"", file=sys.stderr)
        sys.exit(1)
    
    msg = sys.argv[1]
    send_message(msg)
