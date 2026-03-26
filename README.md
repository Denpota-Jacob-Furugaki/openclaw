# OpenClaw Docker Deployment

This repository contains Docker configurations for deploying OpenClaw locally and to AWS.

## 🚀 Quick Start

### Local Development

1. **Prerequisites**
   - Docker Desktop installed
   - Docker Compose installed
   - At least 4GB RAM available

2. **Start OpenClaw**
   ```bash
   docker-compose up -d
   ```

3. **Access OpenClaw**
   - Main interface: http://localhost:8080
   - Canvas: http://localhost:8080/canvas
   - Ollama API: http://localhost:11434

4. **View logs**
   ```bash
   docker-compose logs -f
   ```

5. **Stop services**
   ```bash
   docker-compose down
   ```

## 📱 Telegram Bot Integration

OpenClaw includes a Telegram bot for remote monitoring and control.

### Features
- 🔔 **Notifications**: Deployment alerts, health checks, errors, metrics
- 🎮 **Control**: Start/stop/restart services remotely
- 📊 **Monitoring**: Real-time status, logs, and resource metrics
- 🔒 **Secure**: Authorized access only

### Quick Setup

```bash
# Windows
.\setup-telegram.ps1

# Linux/Mac
chmod +x setup-telegram.sh
./setup-telegram.sh
```

See [TELEGRAM-SETUP.md](TELEGRAM-SETUP.md) for detailed setup instructions.

**Contact**: +81 80 2466 0377

## ☁️ AWS Deployment

See [AWS-DEPLOYMENT.md](AWS-DEPLOYMENT.md) for comprehensive deployment guide.

### Quick Deploy to AWS

```bash
# Configure AWS CLI
aws configure

# Run deployment script
chmod +x aws-deploy.sh
./aws-deploy.sh
```

## 📁 Project Structure

```
.
├── Dockerfile                  # OpenClaw container definition
├── Dockerfile.telegram         # Telegram bot container
├── docker-compose.yml          # Multi-container orchestration
├── nginx.conf                  # Reverse proxy configuration
├── telegram-bot.py             # Telegram bot for control
├── telegram-notify.py          # Notification service
├── telegram-config.json        # Bot configuration (gitignored)
├── setup-telegram.ps1          # Windows bot setup script
├── setup-telegram.sh           # Linux/Mac bot setup script
├── aws-deploy.sh               # Automated AWS deployment script
├── aws-deploy.ps1              # Windows AWS deployment script
├── user-data.sh                # EC2 initialization script
├── AWS-DEPLOYMENT.md           # Detailed AWS deployment guide
├── TELEGRAM-SETUP.md           # Telegram bot setup guide
├── README.md                   # This file
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
├── openclaw.json               # OpenClaw configuration
└── data/                       # Application data directory
```

## 🔧 Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your settings

3. Restart services:
   ```bash
   docker-compose restart
   ```

## 🐳 Docker Commands

```bash
# Build containers
docker-compose build

# Start in foreground (see logs directly)
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f [service_name]

# Restart specific service
docker-compose restart openclaw

# Stop all services
docker-compose down

# Remove all data (CAUTION)
docker-compose down -v

# Access container shell
docker-compose exec openclaw bash
```

## 📊 Monitoring

### Check Container Status
```bash
docker-compose ps
```

### View Resource Usage
```bash
docker stats
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f openclaw
docker-compose logs -f ollama
```

## 🔒 Security Notes

- Change default passwords before deploying to production
- Use environment variables for sensitive data
- Enable HTTPS in production (see AWS-DEPLOYMENT.md)
- Restrict security group rules to specific IPs when possible
- Regularly update Docker images and system packages

## 🐛 Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs openclaw

# Rebuild containers
docker-compose build --no-cache
docker-compose up -d
```

### Port already in use
```bash
# Find process using port 8080
netstat -ano | findstr :8080  # Windows
lsof -i :8080                  # Linux/Mac

# Change port in docker-compose.yml or stop conflicting process
```

### Out of disk space
```bash
# Clean up Docker
docker system prune -a
docker volume prune
```

## 📝 Development

### Making Changes

1. Edit source files
2. Rebuild containers: `docker-compose build`
3. Restart services: `docker-compose up -d`

### Testing

```bash
# Run tests in container
docker-compose exec openclaw npm test

# Or run specific test
docker-compose exec openclaw npm test -- test-name
```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [AWS EC2 Documentation](https://docs.aws.amazon.com/ec2/)
- [Nginx Documentation](https://nginx.org/en/docs/)

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

[Add your license here]

## 🆘 Support

For issues and questions:
- Open an issue on GitHub
- Check AWS-DEPLOYMENT.md for deployment issues
- Review Docker logs for runtime errors

---

**Note**: This setup is configured for the AWS ap-northeast-3 (Osaka) region. Modify AWS_REGION in configuration files if deploying to a different region.
