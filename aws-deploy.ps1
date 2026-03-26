# OpenClaw AWS Deployment Script for Windows PowerShell
# Region: ap-northeast-3 (Osaka)

$ErrorActionPreference = "Stop"

# Configuration
$AWS_REGION = "ap-northeast-3"
$INSTANCE_TYPE = "t3.medium"
$AMI_ID = "ami-0c960bcbab6e0b78b"  # Ubuntu 22.04 LTS in ap-northeast-3
$KEY_NAME = "openclaw-key"
$SECURITY_GROUP_NAME = "openclaw-sg"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "OpenClaw AWS Deployment Script" -ForegroundColor Cyan
Write-Host "Region: $AWS_REGION" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Check if AWS CLI is installed
if (!(Get-Command aws -ErrorAction SilentlyContinue)) {
    Write-Host "Error: AWS CLI is not installed." -ForegroundColor Red
    Write-Host "Please install it from: https://aws.amazon.com/cli/" -ForegroundColor Yellow
    exit 1
}

# Check if AWS CLI is configured
try {
    aws sts get-caller-identity | Out-Null
} catch {
    Write-Host "Error: AWS CLI is not configured." -ForegroundColor Red
    Write-Host "Please run 'aws configure' first." -ForegroundColor Yellow
    exit 1
}

Write-Host "`nStep 1: Creating security group..." -ForegroundColor Green
try {
    $SECURITY_GROUP_ID = (aws ec2 describe-security-groups `
        --group-names $SECURITY_GROUP_NAME `
        --region $AWS_REGION `
        --output text `
        --query 'SecurityGroups[0].GroupId' 2>$null)
    
    if (!$SECURITY_GROUP_ID) {
        $SECURITY_GROUP_ID = (aws ec2 create-security-group `
            --group-name $SECURITY_GROUP_NAME `
            --description "Security group for OpenClaw" `
            --region $AWS_REGION `
            --output text `
            --query 'GroupId')
    }
} catch {
    Write-Host "Error creating security group: $_" -ForegroundColor Red
    exit 1
}

Write-Host "Security Group ID: $SECURITY_GROUP_ID" -ForegroundColor Cyan

Write-Host "`nStep 2: Configuring security group rules..." -ForegroundColor Green
$ports = @(
    @{Port=22; Description="SSH"},
    @{Port=80; Description="HTTP"},
    @{Port=443; Description="HTTPS"},
    @{Port=8080; Description="OpenClaw"}
)

foreach ($portInfo in $ports) {
    try {
        aws ec2 authorize-security-group-ingress `
            --group-id $SECURITY_GROUP_ID `
            --protocol tcp `
            --port $portInfo.Port `
            --cidr 0.0.0.0/0 `
            --region $AWS_REGION 2>$null
        Write-Host "  Added rule: $($portInfo.Description) (port $($portInfo.Port))" -ForegroundColor Gray
    } catch {
        Write-Host "  Rule already exists: $($portInfo.Description)" -ForegroundColor Gray
    }
}

Write-Host "`nStep 3: Creating EC2 key pair..." -ForegroundColor Green
try {
    aws ec2 describe-key-pairs --key-names $KEY_NAME --region $AWS_REGION 2>$null | Out-Null
    Write-Host "Key pair '$KEY_NAME' already exists" -ForegroundColor Yellow
} catch {
    $keyMaterial = aws ec2 create-key-pair `
        --key-name $KEY_NAME `
        --region $AWS_REGION `
        --query 'KeyMaterial' `
        --output text
    
    $keyMaterial | Out-File -FilePath "$KEY_NAME.pem" -Encoding ASCII
    Write-Host "Key pair created and saved to $KEY_NAME.pem" -ForegroundColor Green
}

Write-Host "`nStep 4: Launching EC2 instance..." -ForegroundColor Green
$INSTANCE_ID = (aws ec2 run-instances `
    --image-id $AMI_ID `
    --instance-type $INSTANCE_TYPE `
    --key-name $KEY_NAME `
    --security-group-ids $SECURITY_GROUP_ID `
    --region $AWS_REGION `
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=OpenClaw-Server}]' `
    --user-data file://user-data.sh `
    --block-device-mappings 'DeviceName=/dev/sda1,Ebs={VolumeSize=30,VolumeType=gp3}' `
    --output text `
    --query 'Instances[0].InstanceId')

Write-Host "Instance ID: $INSTANCE_ID" -ForegroundColor Cyan
Write-Host "Waiting for instance to start..." -ForegroundColor Yellow

aws ec2 wait instance-running `
    --instance-ids $INSTANCE_ID `
    --region $AWS_REGION

$PUBLIC_IP = (aws ec2 describe-instances `
    --instance-ids $INSTANCE_ID `
    --region $AWS_REGION `
    --query 'Reservations[0].Instances[0].PublicIpAddress' `
    --output text)

Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Instance ID: $INSTANCE_ID" -ForegroundColor White
Write-Host "Public IP: $PUBLIC_IP" -ForegroundColor White
Write-Host "`nSSH Command (Git Bash/WSL):" -ForegroundColor Yellow
Write-Host "  ssh -i $KEY_NAME.pem ubuntu@$PUBLIC_IP" -ForegroundColor Gray
Write-Host "`nThe instance is being configured." -ForegroundColor Yellow
Write-Host "Please wait 5-10 minutes for the setup to complete." -ForegroundColor Yellow
Write-Host "`nAccess OpenClaw at: http://$PUBLIC_IP" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
