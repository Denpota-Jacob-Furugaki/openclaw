#!/usr/bin/env python3
"""
OpenClaw Daily Report Generator
Sends a comprehensive daily report via Telegram
Schedule with cron: 0 9 * * * python3 telegram-daily-report.py
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timedelta
import requests

# Load configuration
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'telegram-config.json')
with open(CONFIG_FILE, 'r') as f:
    config = json.load(f)

BOT_TOKEN = config['bot']['token']
ADMIN_CHAT_ID = config['admin'].get('chat_id')


def send_telegram(message: str):
    """Send message to Telegram"""
    if not ADMIN_CHAT_ID:
        print("No admin chat ID configured")
        return
    
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            'chat_id': ADMIN_CHAT_ID,
            'text': message,
            'parse_mode': 'Markdown'
        }
        requests.post(url, data=data, timeout=10)
        print("Report sent successfully")
    except Exception as e:
        print(f"Failed to send report: {e}")


def get_uptime():
    """Get container uptime"""
    try:
        result = subprocess.run(
            ['docker', 'ps', '--format', '{{.Names}}\t{{.Status}}'],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"


def get_metrics():
    """Get resource metrics"""
    try:
        result = subprocess.run(
            ['docker', 'stats', '--no-stream', '--format',
             '{{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}'],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"


def get_disk_usage():
    """Get disk usage"""
    try:
        if sys.platform == 'win32':
            import shutil
            total, used, free = shutil.disk_usage('/')
            percent = (used / total) * 100
            return f"{percent:.1f}% used ({used // (1024**3)}GB / {total // (1024**3)}GB)"
        else:
            result = subprocess.run(
                ['df', '-h', '/'],
                capture_output=True,
                text=True,
                timeout=5
            )
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                return lines[1]
            return "Unknown"
    except Exception as e:
        return f"Error: {e}"


def check_services():
    """Check service health"""
    services = {
        'OpenClaw': 'http://localhost:8080/health',
        'Ollama': 'http://localhost:11434/'
    }
    
    results = []
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                results.append(f"✅ {name}: Healthy")
            else:
                results.append(f"⚠️ {name}: Status {response.status_code}")
        except Exception:
            results.append(f"❌ {name}: Down")
    
    return '\n'.join(results)


def generate_report():
    """Generate daily report"""
    now = datetime.now()
    
    report = f"""
📊 **OpenClaw Daily Report**
{now.strftime('%A, %B %d, %Y')}

**🏥 Service Health:**
{check_services()}

**📈 Container Status:**
```
{get_uptime()}
```

**💻 Resource Usage:**
```
{get_metrics()}
```

**💾 Disk Usage:**
{get_disk_usage()}

**📅 Report Time:**
{now.strftime('%H:%M:%S %Z')}

---
*Automated daily report from OpenClaw*
*Contact: +81 80 2466 0377*
"""
    
    return report


if __name__ == '__main__':
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("Please configure bot token first")
        sys.exit(1)
    
    report = generate_report()
    send_telegram(report)
