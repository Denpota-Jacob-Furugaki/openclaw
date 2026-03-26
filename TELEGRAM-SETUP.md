# Telegram Bot Setup Guide

Complete guide for setting up OpenClaw Telegram notifications and control bot.

## 📱 Features

### Notifications
- ✅ Deployment status alerts
- ✅ System health checks
- ✅ Error notifications
- ✅ Usage metrics reports
- ✅ Container status changes

### Control Commands
- 🎮 Start/stop/restart services
- 📊 Check system status
- 📋 View logs
- 🏥 Health checks
- 📈 Resource metrics

## 🚀 Quick Setup

### Step 1: Create Telegram Bot

1. **Open Telegram** and search for [@BotFather](https://t.me/BotFather)

2. **Send** `/newbot` command

3. **Choose a name** for your bot (e.g., "OpenClaw Monitor")

4. **Choose a username** (must end with 'bot', e.g., "openclaw_monitor_bot")

5. **Copy the token** - it looks like:
   ```
   1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

### Step 2: Get Your Chat ID

**Option A: Using the Bot**
1. Start your bot with the token (see Step 3)
2. Send `/start` to your bot
3. The bot will show your Chat ID

**Option B: Using IDBot**
1. Search for [@userinfobot](https://t.me/userinfobot) on Telegram
2. Send any message
3. Copy your Chat ID from the response

### Step 3: Configure OpenClaw

1. **Edit telegram-config.json:**

```json
{
  "bot": {
    "token": "YOUR_BOT_TOKEN_HERE",
    "name": "OpenClaw Bot",
    "description": "OpenClaw monitoring and control bot"
  },
  "admin": {
    "phone": "+81 80 2466 0377",
    "chat_id": "YOUR_CHAT_ID_HERE",
    "username": "YOUR_USERNAME_HERE"
  },
  "notifications": {
    "deployment": true,
    "health_checks": true,
    "errors": true,
    "metrics": true,
    "startup": true,
    "shutdown": true
  },
  "commands": {
    "status": true,
    "logs": true,
    "restart": true,
    "stop": true,
    "start": true,
    "metrics": true,
    "help": true
  },
  "settings": {
    "check_interval": 300,
    "log_lines": 50,
    "max_retries": 3,
    "timeout": 30
  }
}
```

Replace:
- `YOUR_BOT_TOKEN_HERE` with your bot token from Step 1
- `YOUR_CHAT_ID_HERE` with your Chat ID from Step 2
- `YOUR_USERNAME_HERE` with your Telegram username (optional)

### Step 4: Install Python Dependencies

**On Local Machine (Windows):**
```powershell
pip install -r requirements-telegram.txt
```

**On EC2 Instance (Ubuntu):**
```bash
pip3 install -r requirements-telegram.txt
```

### Step 5: Start the Bot

**Option A: Standalone (for testing)**
```bash
# Start bot only
python telegram-bot.py

# Or start monitor only
python telegram-notify.py
```

**Option B: With Docker (recommended)**
```bash
# Start all services including bot
docker-compose up -d

# View bot logs
docker-compose logs -f telegram-bot
docker-compose logs -f telegram-monitor
```

**Option C: On AWS EC2**
```bash
# SSH into instance
ssh -i openclaw-key.pem ubuntu@YOUR_EC2_IP

# Navigate to directory
cd /opt/openclaw

# Copy your config (or edit directly)
nano telegram-config.json

# Install dependencies
pip3 install -r requirements-telegram.txt

# Start with docker-compose
sudo docker-compose up -d telegram-bot telegram-monitor

# Check status
sudo docker-compose ps
```

## 💬 Using the Bot

### Available Commands

```
/start       - Start bot and get your Chat ID
/authorize   - Authorize your account
/status      - Check container status
/logs        - View recent logs (default: openclaw)
/logs [name] - View logs for specific service
/metrics     - Show resource usage
/health      - Run health checks
/restart     - Restart all services
/restart [service] - Restart specific service
/stop [service]    - Stop specific service
/start [service]   - Start specific service
/help        - Show help message
```

### Examples

**Check Status:**
```
/status
```

**View Logs:**
```
/logs
/logs openclaw
/logs ollama
```

**Restart Service:**
```
/restart
/restart ollama
```

**Check Health:**
```
/health
```

**Get Metrics:**
```
/metrics
```

## 🔔 Notification Types

### Deployment Notifications
```
🚀 OpenClaw Bot Started
Time: 2026-03-23 14:30:00
Admin: +81 80 2466 0377
```

### Health Alerts
```
❌ Service Health Check Failed
Service: OpenClaw
Status: down
Details: Connection refused
```

### Container Changes
```
⚠️ Container Status Changed
Name: openclaw
Old: Up 2 hours
New: Restarting (1) 2 seconds ago
```

### Metrics Reports
```
📊 Hourly Metrics Report

openclaw:
  CPU: 15.5%
  Memory: 512MB / 2GB (25%)

openclaw-ollama:
  CPU: 45.2%
  Memory: 1.5GB / 2GB (75%)
```

### Disk Space Warnings
```
💾 Disk Space Warning
Usage: 92.3%
Action: Consider cleaning up or expanding storage
```

## ⚙️ Configuration Options

### Notification Settings

```json
"notifications": {
  "deployment": true,      // Bot start/stop notifications
  "health_checks": true,   // Service health alerts
  "errors": true,          // Error notifications
  "metrics": true,         // Hourly metrics reports
  "startup": true,         // Service startup alerts
  "shutdown": true         // Service shutdown alerts
}
```

### Command Settings

```json
"commands": {
  "status": true,    // Enable /status command
  "logs": true,      // Enable /logs command
  "restart": true,   // Enable /restart command
  "stop": true,      // Enable /stop command
  "start": true,     // Enable /start command
  "metrics": true,   // Enable /metrics command
  "help": true       // Enable /help command
}
```

### Monitoring Settings

```json
"settings": {
  "check_interval": 300,  // Health check interval (seconds)
  "log_lines": 50,        // Number of log lines to show
  "max_retries": 3,       // Max retry attempts
  "timeout": 30           // Request timeout (seconds)
}
```

## 🔒 Security Best Practices

### 1. Protect Your Bot Token
- Never commit `telegram-config.json` to git
- Use environment variables in production
- Rotate tokens if compromised

### 2. Restrict Bot Access
- Only authorized users can use commands
- Use `/authorize` to add users
- Keep Chat IDs private

### 3. Limit Permissions
```json
"commands": {
  "restart": false,  // Disable dangerous commands
  "stop": false,
  "start": false
}
```

### 4. Use HTTPS
- Set up webhook instead of polling (production)
- Enable SSL/TLS for API calls

### 5. Monitor Bot Activity
- Check logs regularly
- Review authorized users
- Set up alerts for unauthorized access

## 🐛 Troubleshooting

### Bot Not Responding

**Check bot is running:**
```bash
docker-compose ps telegram-bot
```

**View logs:**
```bash
docker-compose logs telegram-bot
```

**Restart bot:**
```bash
docker-compose restart telegram-bot
```

### Not Receiving Notifications

**Check configuration:**
```bash
cat telegram-config.json
```

**Verify Chat ID:**
- Send `/start` to your bot
- Check if Chat ID matches config

**Check monitor is running:**
```bash
docker-compose ps telegram-monitor
docker-compose logs telegram-monitor
```

### "Unauthorized" Errors

**Authorize yourself:**
1. Send `/authorize` to bot
2. Bot will confirm authorization
3. Add your Chat ID to config permanently

### Token Errors

**Verify token format:**
- Format: `NUMBER:ALPHANUMERIC`
- Example: `123456789:ABCdefGHI`

**Get new token:**
1. Message @BotFather
2. Send `/token`
3. Select your bot
4. Update config

### Connection Issues

**Check network:**
```bash
ping api.telegram.org
curl https://api.telegram.org/bot<TOKEN>/getMe
```

**Check firewall:**
- Allow outbound HTTPS (443)
- Allow Telegram API access

## 📊 Advanced Features

### Custom Notifications

Create custom notification script:

```python
#!/usr/bin/env python3
from telegram-notify import send_telegram

# Send custom alert
send_telegram("🎉 **Custom Event**\n\nYour custom message here")
```

### Scheduled Reports

Add to crontab:

```bash
# Daily report at 9 AM
0 9 * * * python3 /opt/openclaw/telegram-daily-report.py
```

### Webhook Mode (Production)

For high-traffic bots, use webhooks instead of polling:

```python
# In telegram-bot.py
application.run_webhook(
    listen="0.0.0.0",
    port=8443,
    url_path="telegram",
    webhook_url="https://your-domain.com/telegram"
)
```

### Multi-Admin Support

Add multiple admins:

```json
"admin": {
  "chat_ids": [123456789, 987654321],
  "usernames": ["admin1", "admin2"]
}
```

## 📱 Mobile Management

### Use Telegram App
- iOS: [App Store](https://apps.apple.com/app/telegram-messenger/id686449807)
- Android: [Play Store](https://play.google.com/store/apps/details?id=org.telegram.messenger)

### Quick Actions
1. Pin bot chat for quick access
2. Use bot commands from notifications
3. Set custom notifications
4. Use Telegram Desktop for easier typing

## 🔄 Updates and Maintenance

### Update Bot Code

```bash
# Pull latest changes
git pull

# Rebuild container
docker-compose build telegram-bot

# Restart services
docker-compose up -d telegram-bot
```

### Backup Configuration

```bash
# Backup config
cp telegram-config.json telegram-config.json.backup

# Restore config
cp telegram-config.json.backup telegram-config.json
```

### Rotate Bot Token

1. Get new token from @BotFather
2. Update `telegram-config.json`
3. Restart bot:
   ```bash
   docker-compose restart telegram-bot telegram-monitor
   ```

## 📞 Support

### Common Issues
- Check logs first: `docker-compose logs telegram-bot`
- Verify configuration: `cat telegram-config.json`
- Test bot token: Visit `https://api.telegram.org/bot<TOKEN>/getMe`

### Resources
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [python-telegram-bot docs](https://docs.python-telegram-bot.org/)
- [BotFather commands](https://core.telegram.org/bots#6-botfather)

### Contact
- Phone/Telegram: +81 80 2466 0377
- Bot Username: @your_bot_username

---

**Ready to go!** Send `/start` to your bot to begin. 🚀
