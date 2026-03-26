# Check AWS OpenClaw Status
Write-Host "🦞 Checking AWS instance status..." -ForegroundColor Cyan
Write-Host ""

$instanceId = "i-0b32a1b2a71cee95c"
$region = "ap-northeast-3"

# Get instance details
$instance = aws ec2 describe-instances --instance-ids $instanceId --region $region --query 'Reservations[0].Instances[0]' --output json | ConvertFrom-Json

$status = $instance.State.Name
$ip = $instance.PublicIpAddress
$instanceType = $instance.InstanceType
$launchTime = $instance.LaunchTime

Write-Host "Instance ID: $instanceId" -ForegroundColor Gray
Write-Host "Region: $region" -ForegroundColor Gray
Write-Host "Type: $instanceType" -ForegroundColor Gray
Write-Host ""

if ($status -eq "running") {
    Write-Host "Status: RUNNING ✅" -ForegroundColor Green
    Write-Host "Public IP: $ip" -ForegroundColor Cyan
    Write-Host "Dashboard: http://${ip}:8080" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "💰 Currently costing: ~$0.021/hour" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To stop (save money): .\aws-stop.ps1" -ForegroundColor Gray
    
    # Calculate running time
    $runningTime = (Get-Date) - [DateTime]$launchTime
    Write-Host ""
    Write-Host "Running for: $([int]$runningTime.TotalHours) hours, $($runningTime.Minutes) minutes" -ForegroundColor Gray
    
} elseif ($status -eq "stopped") {
    Write-Host "Status: STOPPED 💤" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "💰 Cost: ~$0.001/hour (storage only)" -ForegroundColor Green
    Write-Host ""
    Write-Host "To start: .\aws-start.ps1" -ForegroundColor Cyan
    
} else {
    Write-Host "Status: $status" -ForegroundColor Yellow
}
