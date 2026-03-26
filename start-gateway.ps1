# Start OpenClaw Gateway with Ollama
# Comprehensive startup script

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  OpenClaw Gateway Startup" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Change to openclaw directory
Set-Location C:\Users\denpo\.openclaw

# Step 1: Check and start Ollama
Write-Host "[1/3] Checking Ollama..." -ForegroundColor Yellow
$ollamaProcess = Get-Process ollama -ErrorAction SilentlyContinue
if (-not $ollamaProcess) {
    Write-Host "      Starting Ollama service..." -ForegroundColor Gray
    Start-Process "ollama" -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 3
    Write-Host "      ✓ Ollama started" -ForegroundColor Green
} else {
    Write-Host "      ✓ Ollama already running" -ForegroundColor Green
}

# Step 2: Show configuration
Write-Host "`n[2/3] Configuration:" -ForegroundColor Yellow
Write-Host "      • Telegram Bot: @DptEngineer_bot" -ForegroundColor Cyan
Write-Host "      • Main agent: Claude Sonnet 4.5 (paid)" -ForegroundColor Yellow
Write-Host "      • Cron agent: Ollama qwen2.5-coder:32b (FREE)" -ForegroundColor Green
Write-Host "      • Port: 8080" -ForegroundColor Gray

# Step 3: Start gateway
Write-Host "`n[3/3] Starting gateway..." -ForegroundColor Yellow
Write-Host "      URL: http://localhost:8080`n" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

npx --no openclaw gateway --port 8080
