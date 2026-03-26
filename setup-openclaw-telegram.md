# OpenClaw + Telegram Integration Setup

## What You Have Now:
✅ Monitoring Bot (running) - Sends alerts, /status, /restart commands
✅ Your Bot Token: 8703712953:AAFhE7U2ekonfoJ9oNAWoyxrLgFk3D7nS_8
✅ Your Chat ID: 8720377858

## Next: Connect OpenClaw AI to Telegram

### Step 1: Get API Key for AI Model

You need an AI model. Choose one:

**Option A: Anthropic Claude (Recommended)**
1. Go to: https://console.anthropic.com/
2. Sign up / Login
3. Add $40 credits (gets you Tier 2 - faster, better)
4. API Keys → Create Key
5. Copy the key (starts with `sk-ant-...`)

**Option B: OpenAI (Alternative)**
1. Go to: https://platform.openai.com/
2. Sign up / Login  
3. Billing → Add credits ($10 minimum)
4. API Keys → Create new secret key
5. Copy the key (starts with `sk-...`)

**Option C: Free Option (Gemini)**
1. Go to: https://ai.google.dev/
2. Get API key (free tier available)

### Step 2: Add API Key to OpenClaw

Create `.env` file in `C:\Users\denpo\.openclaw\`:

```bash
# For Claude
ANTHROPIC_API_KEY=sk-ant-your-key-here

# OR for OpenAI
OPENAI_API_KEY=sk-your-key-here

# Telegram (already configured)
TELEGRAM_BOT_TOKEN=8703712953:AAFhE7U2ekonfoJ9oNAWoyxrLgFk3D7nS_8
TELEGRAM_CHAT_ID=8720377858
```

### Step 3: Configure OpenClaw for Telegram

Edit `openclaw.json` and add Telegram as a channel:

```json
{
  "meta": {
    "lastTouchedVersion": "2026.3.13",
    "lastTouchedAt": "2026-03-24T09:00:00.000Z"
  },
  "agents": {
    "defaults": {
      "model": "anthropic/claude-sonnet-4-5",
      "compaction": {
        "mode": "safeguard"
      }
    }
  },
  "channels": {
    "telegram": {
      "enabled": true,
      "token": "8703712953:AAFhE7U2ekonfoJ9oNAWoyxrLgFk3D7nS_8",
      "allowedUsers": [8720377858]
    }
  },
  "commands": {
    "native": "auto",
    "nativeSkills": "auto",
    "restart": true,
    "ownerDisplay": "raw"
  },
  "gateway": {
    "mode": "local",
    "auth": {
      "mode": "none"
    }
  }
}
```

### Step 4: Start OpenClaw

```powershell
# If OpenClaw isn't running, start it:
cd C:\Users\denpo\.openclaw
# Follow OpenClaw's startup instructions
```

### Step 5: Test Everything

In Telegram, message your bot:
- "Hello" - Test monitoring bot
- Talk to OpenClaw AI (if configured)

## What's Next?

1. **Local Testing** - Test everything works locally
2. **Add Skills** - Gmail, Calendar, etc.
3. **AWS Deployment** - Move to cloud 24/7
4. **Security** - Lock down permissions

## Current Status:

✅ Telegram Bot Created: @OClawDenpota_Bot
✅ Monitoring Bot: Running
✅ Notification Service: Running
⏳ OpenClaw AI: Need API key
⏳ AWS Deployment: Ready when you are

## Contact: +81 80 2466 0377
