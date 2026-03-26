# OpenClaw Quick Start Guide

Get OpenClaw running locally or on AWS in minutes!

## 🚀 Local Quick Start (5 minutes)

### 1. Start OpenClaw

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

### 2. Access OpenClaw

- **Main Interface**: http://localhost:8080
- **Canvas**: http://localhost:8080/canvas
- **Ollama API**: http://localhost:11434

### 3. Set Up Telegram Bot (Optional)

```powershell
# Windows
.\setup-telegram.ps1

# Linux/Mac
./setup-telegram.sh
```

**Done!** 🎉

---

## ☁️ AWS Quick Start (15 minutes)

### 1. Configure AWS CLI

```bash
aws configure
# Enter:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Region: ap-northeast-3
# - Output format: json
```

### 2. Deploy to AWS

```powershell
# Windows
.\aws-deploy.ps1

# Linux/Mac/WSL
chmod +x aws-deploy.sh
./aws-deploy.sh
```

### 3. Wait for Deployment

The script will:
- ✅ Create security group
- ✅ Launch EC2 instance (Ubuntu)
- ✅ Install Docker
- ✅ Start OpenClaw services
- ✅ Show public IP

Wait 5-10 minutes for initialization.

### 4. Access Your Server

```
http://YOUR_PUBLIC_IP
```

**Done!** 🎉

---

## 📱 Telegram Bot Setup (5 minutes)

### 1. Create Bot

1. Open Telegram → Search: **@BotFather**
2. Send: `/newbot`
3. Follow instructions
4. **Copy bot token**

### 2. Run Setup

```powershell
# Windows
.\setup-telegram.ps1

# Linux/Mac
./setup-telegram.sh
```

### 3. Start Bot

```bash
# Local
python telegram-bot.py

# Docker
docker-compose up -d telegram-bot telegram-monitor
```

### 4. Use Bot

1. Open Telegram
2. Search for your bot
3. Send: `/start`
4. Copy your Chat ID
5. Update `telegram-config.json` if needed

**Done!** 🎉

---

## 📋 Common Commands

### Docker

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart service
docker-compose restart openclaw

# Check status
docker-compose ps

# View metrics
docker stats
```

### Telegram Bot

```
/start       - Initialize bot
/status      - Check system status
/logs        - View logs
/metrics     - Resource usage
/health      - Health check
/restart     - Restart services
/help        - Show help
```

### AWS

```bash
# Deploy
./aws-deploy.sh

# SSH into instance
ssh -i openclaw-key.pem ubuntu@PUBLIC_IP

# View EC2 status
aws ec2 describe-instances --region ap-northeast-3
```

---

## 🆘 Need Help?

### Check Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f openclaw
docker-compose logs -f telegram-bot
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart one
docker-compose restart openclaw
```

### Clean Start

```bash
# Stop and remove everything
docker-compose down -v

# Start fresh
docker-compose up -d
```

### Get Support

- 📖 [Full AWS Guide](AWS-DEPLOYMENT.md)
- 📱 [Telegram Setup](TELEGRAM-SETUP.md)
- 📞 Contact: **+81 80 2466 0377**

---

## ✅ Success Checklist

### Local Deployment
- [ ] Docker installed
- [ ] Services running (`docker-compose ps`)
- [ ] OpenClaw accessible (http://localhost:8080)
- [ ] Telegram bot configured (optional)

### AWS Deployment
- [ ] AWS CLI configured
- [ ] EC2 instance running
- [ ] Security group configured
- [ ] OpenClaw accessible via public IP
- [ ] SSH access working

### Telegram Bot
- [ ] Bot created with @BotFather
- [ ] Configuration updated
- [ ] Bot responding to /start
- [ ] Notifications working

---

## 🎯 Next Steps

1. **Customize Configuration**
   - Edit `openclaw.json`
   - Update `telegram-config.json`
   - Modify `docker-compose.yml`

2. **Set Up Domain** (AWS)
   - Configure Route 53
   - Point domain to EC2 IP
   - Set up SSL/TLS

3. **Enable Monitoring**
   - Check Telegram notifications
   - Review health checks
   - Monitor metrics

4. **Secure Your Setup**
   - Change default passwords
   - Restrict security groups
   - Enable HTTPS
   - Set up backups

---

**You're all set!** 🚀

For detailed guides, see:
- [README.md](README.md)
- [AWS-DEPLOYMENT.md](AWS-DEPLOYMENT.md)
- [TELEGRAM-SETUP.md](TELEGRAM-SETUP.md)
