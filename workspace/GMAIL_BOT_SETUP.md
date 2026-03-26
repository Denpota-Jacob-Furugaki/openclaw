# Gmail Job Reply Bot - Setup Guide

Automated bot to handle job search emails from platforms like LinkedIn, Indeed, Wantedly, etc.

## Features

- ✅ Automatically reads unread emails from job platforms
- ✅ AI evaluation of job fit (remote + software/AI/DX roles)
- ✅ Auto-generates personalized replies in your style
- ✅ **Safe Mode:** Creates drafts by default (review before sending)
- ✅ Auto-send mode available (optional)

## Prerequisites

1. **Google Cloud Project** with Gmail API enabled
2. **OAuth 2.0 Credentials** (Desktop app)
3. **OpenAI API Key**

## Setup Steps

### 1. Enable Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **Gmail API**:
   - Navigation Menu → APIs & Services → Library
   - Search "Gmail API" → Enable

### 2. Create OAuth Credentials

1. APIs & Services → Credentials
2. **Create Credentials** → OAuth client ID
3. Application type: **Desktop app**
4. Name: "Gmail Job Bot"
5. Download JSON and save as `google_credentials.json` in the workspace

### 3. Install Dependencies

```bash
pip install --upgrade google-auth-oauthlib google-auth-httplib2 google-api-python-client openai python-dotenv
```

### 4. Configure Bot

Edit `gmail_job_reply_bot.py` if needed:

```python
# Line 27: Set to True to auto-send, False to create drafts
AUTO_SEND = False  # Recommended: keep False until you trust the bot

# Lines 42-57: Add/remove job platform domains
JOB_PLATFORMS = [
    'linkedin.com',
    'indeed.com',
    'wantedly.com',
    # ... add more as needed
]
```

### 5. First Run - Authenticate

```bash
cd C:\Users\denpo\.openclaw\workspace
python gmail_job_reply_bot.py
```

- Browser will open for Google OAuth
- **Allow access** to Gmail
- Token saved to `google_token.json` (keep this file safe!)

### 6. Verify Drafts

After first run:
1. Open Gmail → Drafts
2. Review AI-generated replies
3. Edit if needed
4. Send manually

### 7. Schedule Automated Runs (Optional)

#### Option A: Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task:
   - Name: "Gmail Job Bot"
   - Trigger: Daily at 9:00 AM
   - Action: Start a program
   - Program: `python`
   - Arguments: `C:\Users\denpo\.openclaw\workspace\gmail_job_reply_bot.py`
   - Start in: `C:\Users\denpo\.openclaw\workspace`

#### Option B: OpenClaw Cron

```bash
# Check if your OpenClaw supports cron
openclaw gateway config get | grep -i cron

# If supported, use the cron tool to schedule daily runs
```

Create a cron job via OpenClaw:
```javascript
{
  "name": "Gmail Job Bot",
  "schedule": {
    "kind": "cron",
    "expr": "0 9 * * *",  // Daily at 9 AM
    "tz": "Asia/Tokyo"
  },
  "payload": {
    "kind": "systemEvent",
    "text": "Run gmail job reply bot"
  },
  "sessionTarget": "current"
}
```

## Usage

### Manual Run

```bash
cd C:\Users\denpo\.openclaw\workspace
python gmail_job_reply_bot.py
```

### Check Logs

```bash
# View recent activity
cat gmail_job_bot.log

# Watch live (Windows PowerShell)
Get-Content gmail_job_bot.log -Wait -Tail 20
```

### Review Processed Emails

Bot tracks processed emails in `gmail_processed.json` to avoid duplicates.

To reset (process all emails again):
```bash
rm gmail_processed.json
```

## Configuration

### Auto-Send Mode

⚠️ **Use with caution!** Bot will send replies automatically without your review.

Edit `gmail_job_reply_bot.py`:
```python
AUTO_SEND = True  # Line 27
```

Recommended workflow:
1. Run in draft mode for 1-2 weeks
2. Review generated replies to build trust
3. Enable auto-send only if consistently good

### Add More Job Platforms

Edit `JOB_PLATFORMS` list (lines 42-57):
```python
JOB_PLATFORMS = [
    'linkedin.com',
    'your-new-platform.com',  # Add here
]
```

### Adjust Interest Keywords

Edit `INTEREST_KEYWORDS` (lines 59-72) or `REJECT_KEYWORDS` (lines 74-82) to refine AI evaluation.

## Troubleshooting

### "Missing google_credentials.json"

Download OAuth credentials from Google Cloud Console as described in Step 2.

### "Authentication failed"

1. Delete `google_token.json`
2. Run bot again to re-authenticate
3. Make sure you allow all requested permissions

### "No unread job emails found"

- Check that you have unread emails from job platforms
- Verify `JOB_PLATFORMS` list includes your recruiters' domains
- Try manual Gmail search: `is:unread from:linkedin.com`

### AI generating wrong replies

1. Update your profile in `PROFILE_SUMMARY` (lines 33-41)
2. Adjust keywords in `INTEREST_KEYWORDS` / `REJECT_KEYWORDS`
3. Check logs to see AI reasoning

## Safety Features

1. **Draft Mode Default:** Creates drafts, doesn't send automatically
2. **Processed Tracking:** Never processes the same email twice
3. **Marks as Read:** Prevents duplicate runs on same emails
4. **Detailed Logging:** Full audit trail of all actions
5. **Remote Work Filter:** Auto-declines non-remote roles even if otherwise interesting

## Stats & Monitoring

Bot logs summary after each run:
```
=== Summary ===
Processed: 5
Interested: 2
Declined: 3
Skipped (already done): 10
Errors: 0
Mode: DRAFT
```

## Manual Reply Alternative

If you prefer manual replies, use the templates in `job_reply_templates.md`:

```bash
# View templates
cat job_reply_templates.md
```

## Next Steps

1. **Test run** - Review first batch of drafts
2. **Refine keywords** - Adjust based on results
3. **Schedule automation** - Set up daily runs
4. **Monitor logs** - Check weekly for any issues
5. **Optional:** Enable auto-send after 1-2 weeks of successful drafts

## Questions?

Check the logs first:
```bash
tail -50 gmail_job_bot.log
```

Common issues are logged with clear error messages.
