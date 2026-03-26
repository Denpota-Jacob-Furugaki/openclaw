# OpenClaw AWS Deployment Guide

## Overview
This guide will help you deploy OpenClaw to AWS EC2 in the ap-northeast-3 (Osaka) region using Docker and Ubuntu.

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured
   ```bash
   aws configure
   # Enter your AWS Access Key ID, Secret Access Key, and default region (ap-northeast-3)
   ```
3. **Docker** installed locally (for testing)
4. **Git Bash** or WSL (for running bash scripts on Windows)

## Local Development Setup

### 1. Test Locally with Docker

```bash
# Navigate to the openclaw directory
cd c:\Users\denpo\.openclaw

# Build and start the containers
docker-compose up -d

# Check container status
docker-compose ps

# View logs
docker-compose logs -f

# Access OpenClaw
# Open browser to http://localhost:8080
```

### 2. Stop Local Services

```bash
docker-compose down
```

## AWS Deployment

### Option 1: Automated Deployment (Recommended)

1. **Run the deployment script:**

   ```bash
   # From Git Bash or WSL
   chmod +x aws-deploy.sh
   ./aws-deploy.sh
   ```

2. **Wait for completion** (5-10 minutes)

3. **Access your OpenClaw instance** at the public IP provided

### Option 2: Manual Deployment

#### Step 1: Create Security Group

```bash
aws ec2 create-security-group \
    --group-name openclaw-sg \
    --description "Security group for OpenClaw" \
    --region ap-northeast-3

# Note the SecurityGroupId from the output
```

#### Step 2: Add Security Group Rules

```bash
# Replace sg-xxxxxxxxx with your security group ID
SECURITY_GROUP_ID="sg-xxxxxxxxx"

# Allow SSH
aws ec2 authorize-security-group-ingress \
    --group-id ${SECURITY_GROUP_ID} \
    --protocol tcp --port 22 --cidr 0.0.0.0/0 \
    --region ap-northeast-3

# Allow HTTP
aws ec2 authorize-security-group-ingress \
    --group-id ${SECURITY_GROUP_ID} \
    --protocol tcp --port 80 --cidr 0.0.0.0/0 \
    --region ap-northeast-3

# Allow HTTPS
aws ec2 authorize-security-group-ingress \
    --group-id ${SECURITY_GROUP_ID} \
    --protocol tcp --port 443 --cidr 0.0.0.0/0 \
    --region ap-northeast-3

# Allow OpenClaw port
aws ec2 authorize-security-group-ingress \
    --group-id ${SECURITY_GROUP_ID} \
    --protocol tcp --port 8080 --cidr 0.0.0.0/0 \
    --region ap-northeast-3
```

#### Step 3: Create Key Pair

```bash
aws ec2 create-key-pair \
    --key-name openclaw-key \
    --region ap-northeast-3 \
    --query 'KeyMaterial' \
    --output text > openclaw-key.pem

chmod 400 openclaw-key.pem
```

#### Step 4: Launch EC2 Instance

```bash
# Launch instance (Ubuntu 22.04 LTS)
aws ec2 run-instances \
    --image-id ami-0c960bcbab6e0b78b \
    --instance-type t3.medium \
    --key-name openclaw-key \
    --security-group-ids ${SECURITY_GROUP_ID} \
    --region ap-northeast-3 \
    --user-data file://user-data.sh \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=OpenClaw-Server}]' \
    --block-device-mappings 'DeviceName=/dev/sda1,Ebs={VolumeSize=30,VolumeType=gp3}'
```

#### Step 5: Get Public IP

```bash
# Replace i-xxxxxxxxx with your instance ID
aws ec2 describe-instances \
    --instance-ids i-xxxxxxxxx \
    --region ap-northeast-3 \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text
```

#### Step 6: Connect via SSH

```bash
ssh -i openclaw-key.pem ubuntu@<PUBLIC_IP>
```

## Post-Deployment Configuration

### 1. SSH into the Instance

```bash
ssh -i openclaw-key.pem ubuntu@<PUBLIC_IP>
```

### 2. Upload Your OpenClaw Configuration

```bash
# From your local machine
scp -i openclaw-key.pem -r c:\Users\denpo\.openclaw ubuntu@<PUBLIC_IP>:/opt/openclaw/data
```

### 3. Restart Services

```bash
# On the EC2 instance
cd /opt/openclaw
sudo docker-compose restart
```

### 4. Check Logs

```bash
sudo docker-compose logs -f
```

## Instance Types and Pricing

| Instance Type | vCPU | RAM | Price/hour (ap-northeast-3) | Use Case |
|---------------|------|-----|----------------------------|----------|
| t3.micro | 2 | 1 GB | ~$0.012 | Testing |
| t3.small | 2 | 2 GB | ~$0.024 | Light usage |
| t3.medium | 2 | 4 GB | ~$0.048 | Recommended |
| t3.large | 2 | 8 GB | ~$0.096 | Heavy usage |
| t3.xlarge | 4 | 16 GB | ~$0.192 | Production with Ollama |

*Prices are approximate and may vary. Check AWS pricing page for current rates.*

## Using AWS Console

If you prefer using the AWS Console:

1. Navigate to: https://ap-northeast-3.console.aws.amazon.com/ec2
2. Click **Launch Instance**
3. Configure:
   - **Name**: OpenClaw-Server
   - **AMI**: Ubuntu Server 22.04 LTS
   - **Instance Type**: t3.medium (or higher)
   - **Key Pair**: Create new or select existing
   - **Network Settings**: 
     - Allow SSH (22)
     - Allow HTTP (80)
     - Allow HTTPS (443)
     - Allow Custom TCP (8080)
   - **Storage**: 30 GB gp3
   - **Advanced Details** → User Data: Copy content from `user-data.sh`
4. Click **Launch Instance**
5. Wait for instance to start and note the Public IP

## Domain Setup (Optional)

### Using Route 53

1. Register or transfer domain to Route 53
2. Create hosted zone
3. Create A record pointing to EC2 public IP
4. Update nginx configuration with your domain
5. Install SSL certificate (see SSL section)

## SSL/TLS Setup (HTTPS)

### Using Let's Encrypt (Free)

```bash
# SSH into EC2 instance
ssh -i openclaw-key.pem ubuntu@<PUBLIC_IP>

# Install certbot
sudo apt-get update
sudo apt-get install -y certbot

# Stop nginx temporarily
cd /opt/openclaw
sudo docker-compose stop nginx

# Get certificate
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates
sudo mkdir -p /opt/openclaw/ssl
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem /opt/openclaw/ssl/certificate.crt
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem /opt/openclaw/ssl/private.key

# Update nginx configuration (uncomment HTTPS section)
sudo nano /opt/openclaw/nginx.conf

# Restart services
sudo docker-compose up -d
```

### Auto-renewal Setup

```bash
# Add to crontab
sudo crontab -e

# Add this line for auto-renewal
0 0 * * 0 certbot renew && docker-compose -f /opt/openclaw/docker-compose.yml restart nginx
```

## Monitoring and Maintenance

### Check Instance Status

```bash
# From local machine
aws ec2 describe-instance-status \
    --instance-ids i-xxxxxxxxx \
    --region ap-northeast-3
```

### View Docker Logs

```bash
# SSH into instance
ssh -i openclaw-key.pem ubuntu@<PUBLIC_IP>

# View all logs
sudo docker-compose logs -f

# View specific service logs
sudo docker-compose logs -f openclaw
sudo docker-compose logs -f ollama
```

### Update OpenClaw

```bash
# SSH into instance
cd /opt/openclaw

# Pull latest images
sudo docker-compose pull

# Restart services
sudo docker-compose up -d
```

## Backup Strategy

### Manual Backup

```bash
# SSH into instance
cd /opt/openclaw

# Create backup
sudo tar -czf openclaw-backup-$(date +%Y%m%d).tar.gz data/

# Download backup to local machine
# From local machine:
scp -i openclaw-key.pem ubuntu@<PUBLIC_IP>:/opt/openclaw/openclaw-backup-*.tar.gz ./
```

### Automated Backups

Create AWS Backup plan or use EBS snapshots:

```bash
aws ec2 create-snapshot \
    --volume-id vol-xxxxxxxxx \
    --description "OpenClaw backup $(date)" \
    --region ap-northeast-3
```

## Troubleshooting

### Can't Connect to Instance

1. Check security group rules allow your IP
2. Verify instance is running
3. Check key pair permissions: `chmod 400 openclaw-key.pem`

### OpenClaw Not Accessible

```bash
# SSH into instance and check:
sudo docker-compose ps
sudo docker-compose logs openclaw
sudo systemctl status docker
```

### Out of Memory

- Upgrade instance type
- Add swap space:
  ```bash
  sudo fallocate -l 4G /swapfile
  sudo chmod 600 /swapfile
  sudo mkswap /swapfile
  sudo swapon /swapfile
  echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
  ```

## Cost Optimization

1. **Use Reserved Instances** for long-term deployment (up to 75% savings)
2. **Stop instance when not in use** (you only pay for storage)
3. **Use t3 burstable instances** for variable workloads
4. **Set up billing alerts** in AWS Console
5. **Use Spot Instances** for non-critical workloads (up to 90% savings)

## Security Best Practices

1. **Restrict SSH access** to your IP only
2. **Use IAM roles** instead of access keys where possible
3. **Enable CloudWatch logs**
4. **Regular security updates**:
   ```bash
   sudo apt-get update && sudo apt-get upgrade -y
   ```
5. **Use VPC** for network isolation
6. **Enable AWS GuardDuty** for threat detection

## Cleanup

### Delete All Resources

```bash
# Terminate instance
aws ec2 terminate-instances \
    --instance-ids i-xxxxxxxxx \
    --region ap-northeast-3

# Delete security group (after instance terminates)
aws ec2 delete-security-group \
    --group-id sg-xxxxxxxxx \
    --region ap-northeast-3

# Delete key pair
aws ec2 delete-key-pair \
    --key-name openclaw-key \
    --region ap-northeast-3

# Remove local key file
rm openclaw-key.pem
```

## Support and Resources

- AWS EC2 Documentation: https://docs.aws.amazon.com/ec2/
- Docker Documentation: https://docs.docker.com/
- AWS Pricing Calculator: https://calculator.aws/
- AWS Support: https://console.aws.amazon.com/support/

## Next Steps

1. Deploy to AWS using automated script
2. Configure domain name and SSL
3. Set up monitoring and alerts
4. Configure automated backups
5. Customize OpenClaw configuration for your needs
