#!/usr/bin/env python3
"""
OpenClaw Telegram Notification Service
Monitors system and sends alerts
"""

import os
import sys
import json
import time
import logging
import subprocess
from datetime import datetime
import requests

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load configuration
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'telegram-config.json')
with open(CONFIG_FILE, 'r') as f:
    config = json.load(f)

BOT_TOKEN = config['bot']['token']
ADMIN_CHAT_ID = config['admin'].get('chat_id')
CHECK_INTERVAL = config['settings']['check_interval']

# State tracking
last_status = {}


def send_telegram(message: str, parse_mode: str = 'Markdown'):
    """Send message to Telegram"""
    if not ADMIN_CHAT_ID:
        logger.warning("No admin chat ID configured")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            'chat_id': ADMIN_CHAT_ID,
            'text': message,
            'parse_mode': parse_mode,
            'disable_notification': False
        }
        response = requests.post(url, data=data, timeout=10)
        response.raise_for_status()
        logger.info("Telegram message sent")
        return True
    except Exception as e:
        logger.error(f"Failed to send Telegram message: {e}")
        return False


def check_container_health():
    """Check Docker container health"""
    try:
        result = subprocess.run(
            ['docker', 'ps', '--format', '{{.Names}}\t{{.Status}}'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        containers = {}
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split('\t')
                if len(parts) == 2:
                    name, status = parts
                    containers[name] = status
        
        return containers
    except Exception as e:
        logger.error(f"Error checking containers: {e}")
        return {}


def check_service_health():
    """Check service endpoints"""
    services = {
        'OpenClaw': 'http://localhost:8080/health',
        'Ollama': 'http://localhost:11434/'
    }
    
    results = {}
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            results[name] = {
                'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                'code': response.status_code
            }
        except Exception as e:
            results[name] = {
                'status': 'down',
                'error': str(e)
            }
    
    return results


def get_system_metrics():
    """Get system resource metrics"""
    try:
        result = subprocess.run(
            ['docker', 'stats', '--no-stream', '--format',
             '{{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        metrics = {}
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split('\t')
                if len(parts) == 4:
                    name, cpu, mem_usage, mem_perc = parts
                    metrics[name] = {
                        'cpu': cpu,
                        'memory_usage': mem_usage,
                        'memory_percent': mem_perc
                    }
        
        return metrics
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        return {}


def check_disk_space():
    """Check disk space"""
    try:
        if sys.platform == 'win32':
            # Windows
            import shutil
            total, used, free = shutil.disk_usage('/')
            percent = (used / total) * 100
        else:
            # Linux
            result = subprocess.run(
                ['df', '-h', '/'],
                capture_output=True,
                text=True,
                timeout=5
            )
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                percent = float(parts[4].rstrip('%'))
            else:
                percent = 0
        
        return percent
    except Exception as e:
        logger.error(f"Error checking disk space: {e}")
        return 0


def monitor_loop():
    """Main monitoring loop"""
    global last_status
    
    logger.info("Starting monitoring service...")
    
    # Send startup notification
    if config['notifications']['startup']:
        send_telegram(
            f"🚀 **OpenClaw Monitoring Started**\n\n"
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Check Interval: {CHECK_INTERVAL}s"
        )
    
    while True:
        try:
            # Check containers
            containers = check_container_health()
            
            # Detect container changes
            for name, status in containers.items():
                if name not in last_status:
                    if config['notifications']['deployment']:
                        send_telegram(f"🆕 **New Container Detected**\n\nName: {name}\nStatus: {status}")
                elif last_status[name] != status:
                    if 'Up' in status:
                        send_telegram(f"✅ **Container Recovered**\n\nName: {name}\nStatus: {status}")
                    else:
                        send_telegram(f"⚠️ **Container Status Changed**\n\nName: {name}\nOld: {last_status[name]}\nNew: {status}")
            
            # Detect removed containers
            for name in last_status:
                if name not in containers:
                    send_telegram(f"🛑 **Container Stopped**\n\nName: {name}")
            
            last_status = containers.copy()
            
            # Health checks
            if config['notifications']['health_checks']:
                services = check_service_health()
                for name, info in services.items():
                    if info['status'] != 'healthy':
                        send_telegram(
                            f"❌ **Service Health Check Failed**\n\n"
                            f"Service: {name}\n"
                            f"Status: {info['status']}\n"
                            f"Details: {info.get('error', info.get('code', 'Unknown'))}"
                        )
            
            # Check disk space
            disk_percent = check_disk_space()
            if disk_percent > 90:
                send_telegram(
                    f"💾 **Disk Space Warning**\n\n"
                    f"Usage: {disk_percent:.1f}%\n"
                    f"Action: Consider cleaning up or expanding storage"
                )
            
            # Metrics reporting (periodic)
            current_time = datetime.now()
            if config['notifications']['metrics'] and current_time.minute % 60 == 0:
                metrics = get_system_metrics()
                if metrics:
                    metrics_text = "📊 **Hourly Metrics Report**\n\n"
                    for name, data in metrics.items():
                        metrics_text += f"**{name}:**\n"
                        metrics_text += f"  CPU: {data['cpu']}\n"
                        metrics_text += f"  Memory: {data['memory_usage']} ({data['memory_percent']})\n\n"
                    send_telegram(metrics_text)
            
            logger.info(f"Health check completed at {current_time.strftime('%H:%M:%S')}")
            
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
            if config['notifications']['errors']:
                send_telegram(f"❌ **Monitoring Error**\n\n{str(e)}")
        
        time.sleep(CHECK_INTERVAL)


if __name__ == '__main__':
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ Please configure your bot token in telegram-config.json")
        sys.exit(1)
    
    try:
        monitor_loop()
    except KeyboardInterrupt:
        logger.info("Monitoring service stopped by user")
        if config['notifications']['shutdown']:
            send_telegram("🛑 **OpenClaw Monitoring Stopped**")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        send_telegram(f"💥 **Monitoring Service Crashed**\n\n{str(e)}")
