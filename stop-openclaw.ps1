# Stop all OpenClaw and Telegram services

Write-Host "Stopping OpenClaw services..." -ForegroundColor Yellow

# Find and stop Python processes running our bots
$bots = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $cmd = (Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)").CommandLine
    $cmd -like "*telegram-bot.py*" -or $cmd -like "*telegram-notify.py*" -or $cmd -like "*openclaw*"
}

if ($bots) {
    Write-Host "Stopping $($bots.Count) process(es)..." -ForegroundColor Yellow
    $bots | Stop-Process -Force
    Start-Sleep -Seconds 2
    Write-Host "✅ All services stopped" -ForegroundColor Green
} else {
    Write-Host "ℹ️  No services running" -ForegroundColor Gray
}
