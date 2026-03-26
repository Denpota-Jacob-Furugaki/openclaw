# Start OpenClaw Gateway Locally
Write-Host "🦞 Starting OpenClaw locally..." -ForegroundColor Cyan

Set-Location C:\Users\denpo\.openclaw

Write-Host "✅ Starting gateway on http://localhost:8080" -ForegroundColor Green
Write-Host "📱 Telegram bot: @OClawDenpota_Bot" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray

npx --no openclaw gateway --port 8080
