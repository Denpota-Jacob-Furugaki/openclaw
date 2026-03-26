# OpenClaw Hybrid Setup: Local + AWS (Cost-Optimized)

## 💰 Cost Breakdown

### Local (Windows)
- **Cost**: $0/month
- **Use for**: Development, testing, personal use
- **Access**: http://localhost:8080
- **Uptime**: Only when your PC is on

### AWS (ap-northeast-3)
- **Cost**: ~$15-20/month if running 24/7
- **Instance**: t3.small (~$0.0208/hour = $15.18/month)
- **Storage**: 8GB (~$0.80/month)
- **Data transfer**: First 100GB free
- **Use for**: Production, 24/7 access, public demos
- **Access**: http://15.168.143.250:8080

## 🎯 Money-Saving Workflow

### Option 1: Stop/Start AWS When Needed
```powershell
# Start AWS instance (when you need it)
aws ec2 start-instances --instance-ids i-0b32a1b2a71cee95c --region ap-northeast-3

# Wait for it to start
aws ec2 wait instance-running --instance-ids i-0b32a1b2a71cee95c --region ap-northeast-3

# Get new IP (elastic IP costs $3.60/month, but dynamic IP is free)
aws ec2 describe-instances --instance-ids i-0b32a1b2a71cee95c --region ap-northeast-3 --query 'Reservations[0].Instances[0].PublicIpAddress' --output text

# Stop AWS instance (when done)
aws ec2 stop-instances --instance-ids i-0b32a1b2a71cee95c --region ap-northeast-3
```

**Savings**: If you stop instance when not needed:
- Running 8 hours/day: ~$5/month (67% savings!)
- Running weekends only: ~$2.50/month (83% savings!)
- Stopped instances: Only pay for storage ($0.80/month)

### Option 2: Terminate When Not Needed
```powershell
# Terminate instance (delete it completely)
aws ec2 terminate-instances --instance-ids i-0b32a1b2a71cee95c --region ap-northeast-3

# Cost when terminated: $0
# Re-launch later with automation (see below)
```

## 🚀 Quick Commands

### Local (Windows)
```powershell
# Start OpenClaw locally
cd C:\Users\denpo\.openclaw
npx --no openclaw gateway --port 8080

# Or use a background process
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\Users\denpo\.openclaw; npx --no openclaw gateway --port 8080"

# Access
http://localhost:8080
```

### AWS Control
```powershell
# Check instance status
aws ec2 describe-instances --instance-ids i-0b32a1b2a71cee95c --region ap-northeast-3 --query 'Reservations[0].Instances[0].State.Name' --output text

# Start instance
aws ec2 start-instances --instance-ids i-0b32a1b2a71cee95c --region ap-northeast-3

# Stop instance (saves money!)
aws ec2 stop-instances --instance-ids i-0b32a1b2a71cee95c --region ap-northeast-3

# Get current IP
aws ec2 describe-instances --instance-ids i-0b32a1b2a71cee95c --region ap-northeast-3 --query 'Reservations[0].Instances[0].PublicIpAddress' --output text
```

## 📅 Recommended Schedule

**Weekdays** (Development):
- Use **local** (free)
- Stop AWS instance

**Weekends/Demos** (Production):
- Use **AWS** for 24/7 access
- Keep running only when needed

**Result**: ~$2-5/month instead of $15-20/month

## 🔧 Quick Deploy to AWS (When Needed)

### Method 1: EC2 Instance Connect (Browser)
1. Start instance: `aws ec2 start-instances --instance-ids i-0b32a1b2a71cee95c --region ap-northeast-3`
2. Wait 30 seconds
3. Open: https://ap-northeast-3.console.aws.amazon.com/ec2/home?region=ap-northeast-3#ConnectToInstance:instanceId=i-0b32a1b2a71cee95c
4. Click "Connect"
5. Paste deployment script (see below)

### Method 2: One-Line Deploy
```bash
# In EC2 terminal
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo bash - && \
sudo apt-get install -y nodejs && \
npm install openclaw && \
mkdir -p ~/.openclaw/agents/main/agent && \
cat > ~/.openclaw/.env << 'EOF'
ANTHROPIC_API_KEY=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
TELEGRAM_BOT_TOKEN=8703712953:AAFhE7U2ekonfoJ9oNAWoyxrLgFk3D7nS_8
EOF
sudo npm install -g pm2 && \
cd ~/.openclaw && \
pm2 start "npx --no openclaw gateway --port 8080" --name openclaw && \
pm2 save && \
pm2 startup | tail -1 | sudo bash
```

## 💡 Pro Tips

### 1. Use Elastic IP (Optional - $3.60/month)
- Keeps same IP address when stopping/starting
- Worth it if you share the URL frequently
```powershell
# Allocate elastic IP
aws ec2 allocate-address --region ap-northeast-3

# Associate with instance
aws ec2 associate-address --instance-id i-0b32a1b2a71cee95c --allocation-id <ALLOCATION_ID> --region ap-northeast-3
```

### 2. Auto-Stop with CloudWatch (Free)
Create a Lambda function to auto-stop instance at night:
- Stop at 11 PM daily
- Start at 8 AM on weekends
- Saves ~50% automatically

### 3. Sync Configs
Keep your local and AWS configs in sync:
```powershell
# Backup local config
Copy-Item C:\Users\denpo\.openclaw\openclaw.json C:\Users\denpo\.openclaw\openclaw.json.backup

# Upload to AWS (when connected via SSH)
scp -i openclaw-key.pem openclaw.json ubuntu@15.168.143.250:~/.openclaw/
```

## 📊 Cost Comparison

| Scenario | Hours/Month | Cost |
|----------|-------------|------|
| 24/7 Always On | 730 | $15.18 |
| Weekdays 9-5 | 160 | $3.33 |
| Weekends Only | 208 | $4.33 |
| Stopped (storage only) | 0 | $0.80 |
| Local Windows | ∞ | $0.00 |

## 🎮 Your Workflow

**Daily**: Use local (free)
- `npx --no openclaw gateway --port 8080`
- Access: http://localhost:8080

**When you need public access**:
1. Start AWS: `aws ec2 start-instances --instance-ids i-0b32a1b2a71cee95c --region ap-northeast-3`
2. Wait 1 minute
3. Get IP: `aws ec2 describe-instances --instance-ids i-0b32a1b2a71cee95c --region ap-northeast-3 --query 'Reservations[0].Instances[0].PublicIpAddress' --output text`
4. Access: http://<NEW_IP>:8080

**When done**:
- Stop AWS: `aws ec2 stop-instances --instance-ids i-0b32a1b2a71cee95c --region ap-northeast-3`

**Result**: Best of both worlds + massive savings!
