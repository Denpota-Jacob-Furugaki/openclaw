# OpenClaw Telegram Bot Setup Script for Windows
# This script helps you set up the Telegram bot interactively

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "OpenClaw Telegram Bot Setup" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check if telegram-config.json exists
if (Test-Path "telegram-config.json") {
    Write-Host "⚠️  telegram-config.json already exists!" -ForegroundColor Yellow
    $overwrite = Read-Host "Do you want to reconfigure it? (y/N)"
    if ($overwrite -ne "y" -and $overwrite -ne "Y") {
        Write-Host "Setup cancelled." -ForegroundColor Yellow
        exit 0
    }
}

Write-Host "📱 Step 1: Create Telegram Bot" -ForegroundColor Green
Write-Host ""
Write-Host "1. Open Telegram and search for @BotFather" -ForegroundColor Gray
Write-Host "2. Send: /newbot" -ForegroundColor Gray
Write-Host "3. Follow instructions to create your bot" -ForegroundColor Gray
Write-Host "4. Copy the bot token" -ForegroundColor Gray
Write-Host ""

$botToken = Read-Host "Enter your bot token"

if ([string]::IsNullOrWhiteSpace($botToken)) {
    Write-Host "❌ Bot token is required!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "💬 Step 2: Get Your Chat ID" -ForegroundColor Green
Write-Host ""
Write-Host "Option A: Search for @userinfobot and send any message" -ForegroundColor Gray
Write-Host "Option B: Skip this step and the bot will show your ID when you /start it" -ForegroundColor Gray
Write-Host ""

$chatId = Read-Host "Enter your Chat ID (or press Enter to skip)"

Write-Host ""
Write-Host "👤 Step 3: Additional Info (Optional)" -ForegroundColor Green
Write-Host ""

$username = Read-Host "Enter your Telegram username (optional, press Enter to skip)"

if ([string]::IsNullOrWhiteSpace($chatId)) {
    $chatId = "YOUR_CHAT_ID_HERE"
}

if ([string]::IsNullOrWhiteSpace($username)) {
    $username = "YOUR_USERNAME_HERE"
}

# Create configuration
$config = @{
    bot = @{
        token = $botToken
        name = "OpenClaw Bot"
        description = "OpenClaw monitoring and control bot"
    }
    admin = @{
        phone = "+81 80 2466 0377"
        chat_id = $chatId
        username = $username
    }
    notifications = @{
        deployment = $true
        health_checks = $true
        errors = $true
        metrics = $true
        startup = $true
        shutdown = $true
    }
    commands = @{
        status = $true
        logs = $true
        restart = $true
        stop = $true
        start = $true
        metrics = $true
        help = $true
    }
    settings = @{
        check_interval = 300
        log_lines = 50
        max_retries = 3
        timeout = 30
    }
}

# Save configuration
$config | ConvertTo-Json -Depth 10 | Out-File -FilePath "telegram-config.json" -Encoding UTF8

Write-Host ""
Write-Host "✅ Configuration saved to telegram-config.json" -ForegroundColor Green
Write-Host ""

# Check if Python is installed
Write-Host "🐍 Step 4: Install Python Dependencies" -ForegroundColor Green
Write-Host ""

if (Get-Command python -ErrorAction SilentlyContinue) {
    Write-Host "Python found!" -ForegroundColor Green
    $installDeps = Read-Host "Install dependencies now? (Y/n)"
    
    if ($installDeps -ne "n" -and $installDeps -ne "N") {
        Write-Host "Installing dependencies..." -ForegroundColor Yellow
        python -m pip install -r requirements-telegram.txt
        Write-Host "✅ Dependencies installed!" -ForegroundColor Green
    }
} else {
    Write-Host "⚠️  Python not found. Please install Python 3.8+ first." -ForegroundColor Yellow
    Write-Host "Download from: https://www.python.org/downloads/" -ForegroundColor Gray
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 Next Steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Test the bot:" -ForegroundColor White
Write-Host "   python telegram-bot.py" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Open Telegram and send /start to your bot" -ForegroundColor White
Write-Host ""
Write-Host "3. If you skipped Chat ID, copy it from the bot and update:" -ForegroundColor White
Write-Host "   telegram-config.json" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Start with Docker:" -ForegroundColor White
Write-Host "   docker-compose up -d telegram-bot telegram-monitor" -ForegroundColor Gray
Write-Host ""
Write-Host "For more details, see: TELEGRAM-SETUP.md" -ForegroundColor Cyan
Write-Host ""
