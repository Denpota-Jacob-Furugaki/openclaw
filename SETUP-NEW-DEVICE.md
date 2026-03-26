# Setting Up OpenClaw on a New Device

This guide helps you set up OpenClaw on a different computer after cloning from GitHub.

## Prerequisites

- Git installed
- Node.js (v16 or higher)
- Python 3.8+
- Docker (optional, for containerized deployment)

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Denpota-Jacob-Furugaki/openclaw.git
cd openclaw
```

### 2. Install Dependencies

**Node.js dependencies:**
```bash
npm install
```

**Python dependencies:**
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

pip install -r requirements-telegram.txt
```

### 3. Configure Sensitive Files

The following files are gitignored and must be created manually:

#### A. Create `.env` file

Copy the example and fill in your values:
```bash
cp .env.example .env
```

Edit `.env` with your API keys:
```env
ANTHROPIC_API_KEY=sk-ant-xxx
OPENAI_API_KEY=sk-xxx
TELEGRAM_BOT_TOKEN=xxx
TELEGRAM_CHAT_ID=xxx
```

#### B. Create `telegram-config.json`

```json
{
  "bot_token": "YOUR_TELEGRAM_BOT_TOKEN",
  "chat_id": "YOUR_TELEGRAM_CHAT_ID",
  "phone_number": "+81 80 2466 0377"
}
```

#### C. Google OAuth Setup

1. **Download credentials:**
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Navigate to APIs & Services > Credentials
   - Download your OAuth 2.0 Client ID as `google_credentials.json`
   - Place it in the openclaw root directory

2. **First-time authentication:**
   - Run any Google integration script (e.g., `python google_gmail.py`)
   - It will open a browser for OAuth consent
   - After authorization, `google_token.json` will be created automatically

#### D. Gateway Command (Windows)

Create `gateway.cmd`:
```cmd
@echo off
set ANTHROPIC_API_KEY=sk-ant-xxx
set OPENAI_API_KEY=sk-xxx
node server.js
```

### 4. Configure openclaw.json

The `openclaw.json` file is in the repository, but verify these settings:

```json
{
  "agents": {
    "main": {
      "model": "anthropic:claude-sonnet-4.5",
      "apiKey": "${ANTHROPIC_API_KEY}"
    },
    "cron": {
      "model": "ollama:qwen2.5-coder:32b",
      "endpoint": "http://localhost:11434"
    }
  }
}
```

### 5. Start the Application

**Local mode:**
```bash
# Windows
.\start-local.ps1

# Linux/Mac
./start-local.sh
```

**With Telegram bot:**
```bash
python telegram-bot.py
```

## Recommended: Secure Secrets Management

### Option 1: Use a Password Manager

Store your secrets in a password manager (1Password, Bitwarden, etc.) and copy them when setting up a new device.

### Option 2: Use Environment Variables System-wide

**Windows:**
```powershell
[System.Environment]::SetEnvironmentVariable('ANTHROPIC_API_KEY', 'sk-ant-xxx', 'User')
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'sk-xxx', 'User')
```

**Linux/Mac:**
Add to `~/.bashrc` or `~/.zshrc`:
```bash
export ANTHROPIC_API_KEY=sk-ant-xxx
export OPENAI_API_KEY=sk-xxx
export TELEGRAM_BOT_TOKEN=xxx
export TELEGRAM_CHAT_ID=xxx
```

### Option 3: Use a Secrets File (Not in Repo)

Create a separate private repository or use cloud storage for a secrets file:

`secrets/openclaw-secrets.json`:
```json
{
  "anthropic_api_key": "sk-ant-xxx",
  "openai_api_key": "sk-xxx",
  "telegram_bot_token": "xxx",
  "telegram_chat_id": "xxx",
  "google_credentials": {...},
  "google_token": {...}
}
```

Keep this in a **private** location (not in any public repo).

## Files You Need to Recreate

- ✅ **In GitHub:** All code, configs (without secrets), documentation
- ❌ **Not in GitHub (recreate manually):**
  - `.env`
  - `telegram-config.json`
  - `google_credentials.json`
  - `google_token.json`
  - `gateway.cmd`
  - `ec2-setup.sh`
  - `user-data.sh`
  - `DEPLOY-NOW.txt`
  - Agent session files (auto-generated)

## Verification Checklist

After setup, verify:

- [ ] Node.js dependencies installed (`node_modules/` exists)
- [ ] Python environment activated
- [ ] `.env` file exists with all required keys
- [ ] `telegram-config.json` configured
- [ ] Google OAuth credentials in place
- [ ] `openclaw.json` references correct model endpoints
- [ ] Can start local server: `node server.js`
- [ ] Can run Telegram bot: `python telegram-bot.py`
- [ ] Google integrations work (test with `python google_gmail.py`)

## Troubleshooting

**"Module not found" errors:**
```bash
npm install
pip install -r requirements-telegram.txt
```

**Google OAuth not working:**
- Delete old `google_token.json`
- Run authentication flow again
- Make sure `google_credentials.json` is valid

**Telegram bot not responding:**
- Verify `telegram-config.json` has correct bot token
- Check chat_id matches your Telegram user ID
- Test with: `python test-telegram.ps1`

**API key errors:**
- Check `.env` file exists and has valid keys
- Verify environment variables are loaded
- Restart terminal/application after setting env vars

## Security Best Practices

1. **Never commit secrets to git** - Already handled by `.gitignore`
2. **Use different API keys per environment** - Consider separate keys for dev/prod
3. **Rotate tokens periodically** - Especially Google OAuth tokens
4. **Keep backups secure** - Store encrypted backups of config files
5. **Use MFA** - Enable 2FA on all service accounts (GitHub, Google, etc.)

## Next Steps

- Review [README.md](README.md) for full documentation
- Check [TELEGRAM-SETUP.md](TELEGRAM-SETUP.md) for Telegram bot setup
- See [AWS-DEPLOYMENT.md](AWS-DEPLOYMENT.md) for cloud deployment
- Read [QUICKSTART.md](QUICKSTART.md) for usage examples
