# Start OpenClaw with Telegram Integration
# This script starts all OpenClaw services

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Starting OpenClaw + Telegram Bots" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Load environment variables from .env
if (Test-Path ".env") {
    Get-Content .env | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            if ($name -and $name -notmatch '^#') {
                [Environment]::SetEnvironmentVariable($name, $value, "Process")
                Write-Host "✓ Loaded: $name" -ForegroundColor Green
            }
        }
    }
    Write-Host ""
}

# Check if bots are already running
$runningBots = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $cmd = (Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)").CommandLine
    $cmd -like "*telegram-bot.py*" -or $cmd -like "*telegram-notify.py*"
}

if ($runningBots) {
    Write-Host "⚠️  Telegram bots are already running" -ForegroundColor Yellow
    $restart = Read-Host "Restart them? (y/N)"
    if ($restart -eq "y" -or $restart -eq "Y") {
        $runningBots | Stop-Process -Force
        Write-Host "✓ Stopped old bots" -ForegroundColor Green
        Start-Sleep -Seconds 2
    }
}

# Start Telegram Bot
Write-Host "Starting Telegram Control Bot..." -ForegroundColor Yellow
Start-Process python -ArgumentList "telegram-bot.py" -WorkingDirectory $PWD -WindowStyle Hidden
Start-Sleep -Seconds 2

# Start Notification Monitor
Write-Host "Starting Telegram Notification Monitor..." -ForegroundColor Yellow
Start-Process python -ArgumentList "telegram-notify.py" -WorkingDirectory $PWD -WindowStyle Hidden
Start-Sleep -Seconds 2

# Check status
$newBots = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $_.StartTime -gt (Get-Date).AddSeconds(-10)
}

if ($newBots) {
    Write-Host ""
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host "✅ Services Started Successfully!" -ForegroundColor Green
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Running processes:" -ForegroundColor White
    $newBots | Select-Object Id, ProcessName, StartTime | Format-Table -AutoSize
    Write-Host ""
    Write-Host "📱 Check Telegram for notifications!" -ForegroundColor Cyan
    Write-Host "Bot: @OClawDenpota_Bot" -ForegroundColor Gray
    Write-Host "Your Chat ID: 8720377858" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Try these commands in Telegram:" -ForegroundColor Yellow
    Write-Host "  /status  - Check system status" -ForegroundColor Gray
    Write-Host "  /health  - Health check" -ForegroundColor Gray
    Write-Host "  /help    - Show all commands" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ Failed to start services" -ForegroundColor Red
    Write-Host "Check logs for errors" -ForegroundColor Yellow
}

Write-Host "Contact: +81 80 2466 0377" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
