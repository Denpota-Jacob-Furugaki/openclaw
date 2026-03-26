# Pair Your Telegram with OpenClaw

## Quick Setup

### Step 1: Get Pairing Code
```powershell
cd C:\Users\denpo\.openclaw
npx --no openclaw telegram pair
```

This will show:
- A pairing code (like `ABC-123-XYZ`)
- OR a QR code to scan

### Step 2: Message Your Bot
1. Open Telegram
2. Find your bot: @OClawDenpota_Bot
3. Send: `/start`
4. Send the pairing code: `ABC-123-XYZ`

### Step 3: Verify
Send a test message to your bot - it should respond!

## Alternative: Use Environment Variables

If pairing doesn't work, OpenClaw reads from .env:

```env
TELEGRAM_BOT_TOKEN=8703712953:AAFhE7U2ekonfoJ9oNAWoyxrLgFk3D7nS_8
TELEGRAM_CHAT_ID=8720377858
```

Already in your .env ✅

## Troubleshooting

### Bot not responding?
```powershell
# Check gateway logs
npx --no openclaw logs --follow

# Restart gateway
Stop-Process -Name node -Force
npx --no openclaw gateway --port 8080
```

### Check Telegram status
```powershell
npx --no openclaw telegram status
```

### Test sending message
```powershell
npx --no openclaw message send --channel telegram --to 8720377858 --text "Test"
```

## What Works After Pairing

- Send messages to bot → OpenClaw AI responds
- Ask questions, get help
- Control OpenClaw via Telegram
- Gmail/Calendar integration (after Gmail setup)
