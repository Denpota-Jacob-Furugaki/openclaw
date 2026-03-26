# Telegram Setup Guide for OpenClaw

## 📱 Quick Setup

### Step 1: Create Your Bot

1. Open Telegram and search for **@BotFather**
2. Send: `/newbot`
3. Choose a display name: `Denpo AI Assistant` (or any name you like)
4. Choose a username: `denpo_assistant_bot` (must end in `bot`)
5. **Copy the token** BotFather gives you (format: `123456789:ABC...`)

### Step 2: Configure OpenClaw

Once you have your token, I'll add it to your OpenClaw config.

**Paste your bot token here when ready!**

The config will look like this:

```json
{
  "plugins": {
    "entries": {
      "telegram": {
        "enabled": true,
        "config": {
          "token": "YOUR_BOT_TOKEN_HERE"
        }
      }
    }
  },
  "channels": {
    "telegram": {
      "enabled": true,
      "dmPolicy": "pairing",
      "groupPolicy": "allowlist",
      "streaming": "partial"
    }
  }
}
```

### Step 3: Pair Your Account

After configuring:

1. **Restart OpenClaw** → I'll restart the gateway automatically
2. **Open your Telegram bot** in Telegram app
3. **Send:** `/pair`
4. **Follow the pairing instructions** to link your Telegram account

### Step 4: Start Chatting!

Once paired, you can:
- Send messages directly to your bot
- Use all the same features as web chat
- Get job alerts in Telegram
- Control your automation from mobile

## 🔐 Privacy & Security

- **Direct messages only** by default (dmPolicy: pairing)
- **Group chats require allowlist** (groupPolicy: allowlist)
- **Streaming responses** for better UX

## 📋 What You'll Be Able to Do

✅ Check for interview requests  
✅ Reply to job messages  
✅ Run CrowdWorks handler  
✅ Monitor Gmail  
✅ Get alerts on mobile  
✅ Control everything from Telegram  

---

**Ready? Create your bot and give me the token!** 🤖
