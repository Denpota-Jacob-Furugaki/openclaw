# Test Telegram bot connection
# Sends a test message to verify everything works

Write-Host "Testing Telegram Connection..." -ForegroundColor Cyan
Write-Host ""

# Load config
$config = Get-Content "telegram-config.json" | ConvertFrom-Json
$botToken = $config.bot.token
$chatId = $config.admin.chat_id

if (-not $botToken -or $botToken -eq "YOUR_BOT_TOKEN_HERE") {
    Write-Host "❌ Bot token not configured!" -ForegroundColor Red
    exit 1
}

if (-not $chatId -or $chatId -eq "YOUR_CHAT_ID_HERE") {
    Write-Host "❌ Chat ID not configured!" -ForegroundColor Red
    exit 1
}

# Test message
$message = "🧪 **Test Message**`n`nOpenClaw is configured and ready!`n`nTime: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`nContact: +81 80 2466 0377"

$url = "https://api.telegram.org/bot$botToken/sendMessage"
$body = @{
    chat_id = $chatId
    text = $message
    parse_mode = "Markdown"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri $url -Method Post -Body $body -ContentType "application/json"
    
    if ($response.ok) {
        Write-Host "✅ Test message sent successfully!" -ForegroundColor Green
        Write-Host "Check your Telegram app" -ForegroundColor Yellow
    } else {
        Write-Host "❌ Failed to send message" -ForegroundColor Red
        Write-Host $response | ConvertTo-Json
    }
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
}
