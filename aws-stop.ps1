# Stop AWS OpenClaw Instance (Save Money!)
Write-Host "🦞 Stopping AWS EC2 instance to save money..." -ForegroundColor Cyan

$instanceId = "i-0b32a1b2a71cee95c"
$region = "ap-northeast-3"

# Check current status
$status = aws ec2 describe-instances --instance-ids $instanceId --region $region --query 'Reservations[0].Instances[0].State.Name' --output text

Write-Host "Current status: $status" -ForegroundColor Yellow

if ($status -eq "stopped") {
    Write-Host "✅ Instance already stopped!" -ForegroundColor Green
} elseif ($status -eq "stopping") {
    Write-Host "⏳ Instance is already stopping..." -ForegroundColor Yellow
} else {
    Write-Host "⏳ Stopping instance..." -ForegroundColor Yellow
    aws ec2 stop-instances --instance-ids $instanceId --region $region | Out-Null
    
    Write-Host "✅ Stop command sent!" -ForegroundColor Green
    Write-Host ""
    Write-Host "💰 Cost savings:" -ForegroundColor Green
    Write-Host "   - Running: ~$0.021/hour" -ForegroundColor Gray
    Write-Host "   - Stopped: ~$0.001/hour (storage only)" -ForegroundColor Green
    Write-Host ""
    Write-Host "To start again: .\aws-start.ps1" -ForegroundColor Cyan
}
