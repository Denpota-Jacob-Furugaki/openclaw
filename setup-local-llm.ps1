# Setup Local LLM for OpenClaw
Write-Host "🦙 Setting up Local LLM for OpenClaw..." -ForegroundColor Cyan

# Check if Ollama is installed
try {
    $ollamaVersion = ollama --version
    Write-Host "✅ Ollama installed: $ollamaVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Ollama not found. Installing..." -ForegroundColor Red
    winget install Ollama.Ollama
    Write-Host "⚠️ Restart terminal after installation!" -ForegroundColor Yellow
    exit
}

Write-Host ""
Write-Host "📦 Recommended Models for 32GB RAM:" -ForegroundColor Cyan
Write-Host ""
Write-Host "🏆 Best Quality (Your RAM can handle these!):" -ForegroundColor Green
Write-Host "  1. qwen2.5-coder:32b (20GB) - BEST coding model"
Write-Host "  2. deepseek-r1:32b (20GB) - BEST reasoning"
Write-Host "  3. codestral:22b (13GB) - Professional coding"
Write-Host ""
Write-Host "⚡ Fast & Balanced:" -ForegroundColor Yellow
Write-Host "  4. qwen2.5-coder:14b (8.9GB) - Great coding, faster"
Write-Host "  5. deepseek-r1:14b (8.9GB) - Great reasoning, faster"
Write-Host "  6. llama3.1:70b (Q4) (40GB) - Largest GPT-3.5 equivalent"
Write-Host ""

$choice = Read-Host "Enter number (1-6) or type model name [1 recommended]"

switch ($choice) {
    "1" { $model = "qwen2.5-coder:32b" }
    "2" { $model = "deepseek-r1:32b" }
    "3" { $model = "codestral:22b" }
    "4" { $model = "qwen2.5-coder:14b" }
    "5" { $model = "deepseek-r1:14b" }
    "6" { $model = "llama3.1:70b-instruct-q4_0" }
    "" { $model = "qwen2.5-coder:32b" }
    default { $model = $choice }
}

Write-Host ""
Write-Host "📥 Downloading $model..." -ForegroundColor Cyan
ollama pull $model

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Model downloaded successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🔧 Updating OpenClaw config..." -ForegroundColor Cyan
    
    # Update openclaw.json to use this model
    $configPath = "C:\Users\denpo\.openclaw\openclaw.json"
    $config = Get-Content $configPath | ConvertFrom-Json
    $config.agents.defaults.model = "ollama/$model"
    $config | ConvertTo-Json -Depth 10 | Set-Content $configPath
    
    Write-Host "✅ OpenClaw configured to use ollama/$model" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 Restart gateway to use local model:" -ForegroundColor Cyan
    Write-Host "  Stop-Process -Name node -Force" -ForegroundColor Gray
    Write-Host "  npx --no openclaw gateway --port 8080" -ForegroundColor Gray
    Write-Host ""
    Write-Host "💰 Cost savings: FREE instead of ~`$0.003 per message!" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to download model" -ForegroundColor Red
}
