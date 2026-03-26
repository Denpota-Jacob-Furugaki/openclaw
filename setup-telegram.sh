#!/bin/bash
# OpenClaw Telegram Bot Setup Script for Linux/Mac

set -e

echo "========================================="
echo "OpenClaw Telegram Bot Setup"
echo "========================================="
echo ""

# Check if telegram-config.json exists
if [ -f "telegram-config.json" ]; then
    echo "⚠️  telegram-config.json already exists!"
    read -p "Do you want to reconfigure it? (y/N) " overwrite
    if [[ ! "$overwrite" =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 0
    fi
fi

echo "📱 Step 1: Create Telegram Bot"
echo ""
echo "1. Open Telegram and search for @BotFather"
echo "2. Send: /newbot"
echo "3. Follow instructions to create your bot"
echo "4. Copy the bot token"
echo ""

read -p "Enter your bot token: " bot_token

if [ -z "$bot_token" ]; then
    echo "❌ Bot token is required!"
    exit 1
fi

echo ""
echo "💬 Step 2: Get Your Chat ID"
echo ""
echo "Option A: Search for @userinfobot and send any message"
echo "Option B: Skip this step and the bot will show your ID when you /start it"
echo ""

read -p "Enter your Chat ID (or press Enter to skip): " chat_id

echo ""
echo "👤 Step 3: Additional Info (Optional)"
echo ""

read -p "Enter your Telegram username (optional): " username

[ -z "$chat_id" ] && chat_id="YOUR_CHAT_ID_HERE"
[ -z "$username" ] && username="YOUR_USERNAME_HERE"

# Create configuration
cat > telegram-config.json <<EOF
{
  "bot": {
    "token": "$bot_token",
    "name": "OpenClaw Bot",
    "description": "OpenClaw monitoring and control bot"
  },
  "admin": {
    "phone": "+81 80 2466 0377",
    "chat_id": "$chat_id",
    "username": "$username"
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
EOF

echo ""
echo "✅ Configuration saved to telegram-config.json"
echo ""

# Check if Python is installed
echo "🐍 Step 4: Install Python Dependencies"
echo ""

if command -v python3 &> /dev/null; then
    echo "Python found!"
    read -p "Install dependencies now? (Y/n) " install_deps
    
    if [[ ! "$install_deps" =~ ^[Nn]$ ]]; then
        echo "Installing dependencies..."
        pip3 install -r requirements-telegram.txt
        echo "✅ Dependencies installed!"
    fi
else
    echo "⚠️  Python not found. Please install Python 3.8+ first."
fi

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Test the bot:"
echo "   python3 telegram-bot.py"
echo ""
echo "2. Open Telegram and send /start to your bot"
echo ""
echo "3. If you skipped Chat ID, copy it from the bot and update:"
echo "   telegram-config.json"
echo ""
echo "4. Start with Docker:"
echo "   docker-compose up -d telegram-bot telegram-monitor"
echo ""
echo "For more details, see: TELEGRAM-SETUP.md"
echo ""
