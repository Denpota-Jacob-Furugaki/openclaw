# Start AWS OpenClaw Instance
Write-Host "🦞 Starting AWS EC2 instance..." -ForegroundColor Cyan

$instanceId = "i-0b32a1b2a71cee95c"
$region = "ap-northeast-3"

# Check current status
$status = aws ec2 describe-instances --instance-ids $instanceId --region $region --query 'Reservations[0].Instances[0].State.Name' --output text

Write-Host "Current status: $status" -ForegroundColor Yellow

if ($status -eq "running") {
    Write-Host "✅ Instance already running!" -ForegroundColor Green
} else {
    Write-Host "⏳ Starting instance..." -ForegroundColor Yellow
    aws ec2 start-instances --instance-ids $instanceId --region $region | Out-Null
    
    Write-Host "⏳ Waiting for instance to start (this takes ~30 seconds)..." -ForegroundColor Yellow
    aws ec2 wait instance-running --instance-ids $instanceId --region $region
    
    Write-Host "✅ Instance started!" -ForegroundColor Green
}

# Get IP address
Write-Host ""
Write-Host "Getting public IP address..." -ForegroundColor Cyan
$ip = aws ec2 describe-instances --instance-ids $instanceId --region $region --query 'Reservations[0].Instances[0].PublicIpAddress' --output text

Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host "✅ AWS OpenClaw is running!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host "Dashboard: http://${ip}:8080" -ForegroundColor Cyan
Write-Host "Telegram: @OClawDenpota_Bot" -ForegroundColor Yellow
Write-Host ""
Write-Host "To stop (save money): .\aws-stop.ps1" -ForegroundColor Gray

# Try to open in browser
Start-Process "http://${ip}:8080"
