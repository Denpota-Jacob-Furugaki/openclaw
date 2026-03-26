# Gmail OAuth for OpenClaw

You already have Google OAuth credentials! Just need to connect them.

## ✅ What You Have

- `google_credentials.json` - OAuth app credentials
- `google_token.json` - Your authenticated token
- Python scripts (google_gmail.py, google_calendar.py, google_drive.py)

## 🔌 Connect to OpenClaw

### Option 1: OpenClaw Skills/Plugins

Check if Gmail skill is available:
```powershell
cd C:\Users\denpo\.openclaw
npx --no openclaw skills list | Select-String gmail
npx --no openclaw plugins list | Select-String gmail
```

If found, install:
```powershell
npx --no openclaw skills install gmail
# OR
npx --no openclaw plugins install gmail
```

### Option 2: Custom Integration (Recommended)

Your Python scripts already work! Integrate them:

**1. Create OpenClaw Skill**
```powershell
cd C:\Users\denpo\.openclaw
mkdir -p skills\gmail-control
```

**2. Create skill definition:**
Create `skills\gmail-control\SKILL.md`:
```markdown
# Gmail Control Skill

Tools for reading, searching, and sending emails via Gmail API.

## Commands

### Check inbox
Read recent emails

### Search emails
Search Gmail with query

### Send email
Send email to recipient

## Implementation

Uses existing google_gmail.py module with OAuth2 authentication.
```

**3. Add tool definitions** (optional)

Create `skills\gmail-control\tools.json` to expose Gmail functions to OpenClaw agent.

### Option 3: Direct Python Integration

Keep using your Python scripts via Telegram:

Your **telegram-bot.py** already has Gmail commands:
- `/gmail` - Check inbox
- `/email [id]` - Read email
- `/calendar` - View calendar
- `/sheets` - List spreadsheets
- `/drive` - Browse Drive

**To use:**
```powershell
# Run your Python telegram bot
cd C:\Users\denpo\.openclaw
python telegram-bot.py
```

This runs alongside OpenClaw and gives you Gmail access via Telegram!

## 🎯 Recommended Workflow

**Best of both worlds:**

1. **OpenClaw Gateway** - For AI chat, main interface
   ```powershell
   npx --no openclaw gateway --port 8080
   ```

2. **Python Telegram Bot** - For Gmail/Google commands
   ```powershell
   python telegram-bot.py
   ```

Both run together! Use same bot (@OClawDenpota_Bot):
- General questions → OpenClaw AI
- Gmail/Calendar → Python bot commands

## Test Gmail Integration

```python
# Quick test
python -c "from google_gmail import get_unread_count; print(f'Unread: {get_unread_count()}')"
```

## Gmail Bot Features

Your Python bot supports:
- ✅ Gmail read/send/search
- ✅ Calendar events
- ✅ Calendar invite auto-accept
- ✅ Drive file listing
- ✅ Sheets access

All working via `/gmail`, `/calendar`, etc. commands!
