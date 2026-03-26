# CrowdWorks Automatic Message Handler - Setup Guide

Automatically check CrowdWorks for new proposals and messages, evaluate them, and reply.

## 🚀 Quick Start

### 1. Add Credentials

Edit `.env` file in workspace:

```bash
OPENAI_API_KEY=sk-your-key-here
CROWDWORKS_EMAIL=your-email@example.com
CROWDWORKS_PASSWORD=your-password
CROWDWORKS_AUTO_SEND=false  # false = review mode, true = auto-send
```

### 2. Install Dependencies

```bash
pip install playwright python-dotenv openai
playwright install chromium
```

### 3. Run the Handler

```bash
cd C:\Users\denpo\.openclaw\workspace

# Review mode (generates replies, doesn't send)
python crowdworks_auto_handler.py

# Show browser (debug)
python crowdworks_auto_handler.py --visible
```

### 4. Enable Auto-Send (Optional)

After testing in review mode, enable auto-send:

```bash
# In .env file:
CROWDWORKS_AUTO_SEND=true
```

## 📋 What It Does

1. ✅ Logs into CrowdWorks (saves session)
2. ✅ Checks dashboard for new proposals/messages
3. ✅ Reads each proposal:
   - Job title and description
   - Client name
   - Budget
   - Current status
4. ✅ AI evaluates fit:
   - Remote work requirement
   - Software/AI/DX match
   - Budget considerations
5. ✅ Generates reply in your style
6. ✅ **Review mode** (default): Saves reply to file for review
7. ✅ **Auto-send mode** (optional): Sends reply directly on CrowdWorks

## 🎯 Evaluation Criteria

Same as your other bots:

**✅ Interested:**
- Software engineering, AI/ML, full-stack development
- DX/Digital transformation
- Marketing engineering
- **MUST be remote or mostly remote**

**❌ Decline:**
- Sales, admin, manual labor
- Non-tech roles
- Non-remote positions

## 📊 Output

### Review Mode (Default)

```
🔍 Starting CrowdWorks auto-handler. 5 proposals already processed.
🔍 Auto-send mode: False
✓ Already logged in
📋 Checking for new proposals and messages...
📸 Screenshot saved: crowdworks_dashboard_20260324_143200.png
🔍 Found 8 proposal/message items

[0] Processing proposal 288200154
URL: https://crowdworks.jp/proposals/288200154
Title: ReactとNode.jsを使用したWebアプリ開発
Client: テック株式会社
Budget: ¥300,000 - ¥500,000
AI: interested=True, remote=True, confidence=85%, reason=Full-stack dev project, remote work

=== Generated Reply ===
ご連絡いただきありがとうございます。

ReactとNode.jsを使用したWebアプリ開発案件に大変興味がございます。
フルスタック開発を専門としており、React/Next.js、Node.jsの実装経験が豊富です。

詳細についてお話しできればと思います。

ポートフォリオ：https://denpota-portfolio.vercel.app/

よろしくお願いいたします。
古垣 伝法太
====================

✅ Auto-send disabled. Reply generated but not sent.
📄 Saved to: crowdworks_reply_288200154.txt

=== Summary ===
Processed: 3
Interested: 2
Declined: 1
Skipped (already done): 5
Errors: 0
Mode: DRAFT
```

### Auto-Send Mode

Same output, but:
```
✓ Reply sent automatically
📸 Screenshot: crowdworks_sent_288200154.png
```

## 📁 Files Created

**Per run:**
- `crowdworks_dashboard_YYYYMMDD_HHMMSS.png` - Dashboard screenshot
- `crowdworks_proposal_<ID>_YYYYMMDD_HHMMSS.png` - Proposal page screenshot
- `crowdworks_reply_<ID>.txt` - Generated reply (review mode)
- `crowdworks_sent_<ID>.png` - Confirmation screenshot (auto-send mode)

**Persistent:**
- `crowdworks_processed.json` - Processed proposal IDs (avoid duplicates)
- `platform_sessions/crowdworks_session.json` - Login session
- `crowdworks_auto_handler.log` - Activity log

## ⏰ Scheduling

### Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task:
   - Name: "CrowdWorks Auto Handler"
   - Trigger: Daily at 9:00 AM, 2:00 PM, 6:00 PM
   - Action: Start a program
   - Program: `python`
   - Arguments: `C:\Users\denpo\.openclaw\workspace\crowdworks_auto_handler.py`
   - Start in: `C:\Users\denpo\.openclaw\workspace`

### OpenClaw Cron (if supported)

Ask me to create a cron job for periodic checks.

## 🔄 Workflow

### Conservative (Recommended)

1. **Run handler** → Generates replies, doesn't send
2. **Review replies** → Check `crowdworks_reply_*.txt` files
3. **Manually send** → Log into CrowdWorks, copy/paste, send
4. **After 1-2 weeks** → Enable auto-send if replies are consistently good

### Semi-Automated

1. **Run handler** → Generates replies
2. **Quick review** → Check log for summary
3. **Use platform handler** → For specific proposals:
   ```bash
   python platform_message_handler.py https://crowdworks.jp/proposals/288200154 --auto-reply
   ```

### Fully Automated

1. **Enable auto-send** → `CROWDWORKS_AUTO_SEND=true`
2. **Schedule daily** → Task Scheduler or cron
3. **Monitor logs** → Check `crowdworks_auto_handler.log` weekly

## 🆚 vs Manual Platform Handler

**Auto Handler** (`crowdworks_auto_handler.py`):
- Checks **all** new proposals automatically
- Scans dashboard for unresponded items
- Batch processing (handles multiple at once)
- Best for: Regular monitoring, daily checks

**Manual Platform Handler** (`platform_message_handler.py`):
- Handles **specific URL** you provide
- More detailed extraction
- One proposal at a time
- Best for: Email notifications, specific follow-ups

**Use together:**
- Auto handler for daily sweeps
- Manual handler for important/urgent proposals

## 🔧 Troubleshooting

### "Credentials not found in .env"

Make sure `.env` file exists in workspace with:
```
CROWDWORKS_EMAIL=your-email
CROWDWORKS_PASSWORD=your-password
```

### "Login failed"

1. Check credentials are correct
2. Try logging in manually first
3. Delete: `platform_sessions/crowdworks_session.json`
4. Run with `--visible` to see login page

### "No new proposals found"

- May be none needing response
- Check `crowdworks_processed.json` and delete to reset
- Run with `--visible` to see dashboard

### "Could not find textarea/send button"

- CrowdWorks may have changed UI
- Check screenshots to see page state
- Update selectors in script
- Ask me for help

## 💡 Tips

**First run:**
```bash
# Run in visible mode to see what happens
python crowdworks_auto_handler.py --visible
```

**Reset processed tracking:**
```bash
# To re-process all proposals
rm crowdworks_processed.json
```

**Check logs:**
```bash
# View recent activity
cat crowdworks_auto_handler.log

# Watch live
Get-Content crowdworks_auto_handler.log -Wait -Tail 20
```

**Review generated replies:**
```bash
# Read all generated replies
dir crowdworks_reply_*.txt
cat crowdworks_reply_288200154.txt
```

## 🔐 Security

- Credentials in `.env` (gitignored)
- Session cookies in `platform_sessions/` (local only)
- All activity logged for audit
- Screenshots saved for verification

**Never commit:**
- `.env` file
- `*_session.json` files
- `crowdworks_processed.json` (contains your activity)

## 🎓 Integration with Other Tools

**Complete automation flow:**

```
1. Email arrives → "CrowdWorks proposal"
   ↓
2. Interview monitor detects it
   ↓
3. Alerts you with link
   ↓
4. Auto handler processes it (scheduled)
   OR
   Manual handler processes it (on-demand)
   ↓
5. Reply sent on CrowdWorks
   ↓
6. Client sees your response
```

**All tools work together:**
- `check_interview_with_links.py` - Detects CrowdWorks emails
- `crowdworks_auto_handler.py` - **Batch processes all proposals**
- `platform_message_handler.py` - Handles specific URL
- Existing `crowdworks_bot.py` - Applies to jobs

## ❓ FAQ

**Q: Will this interfere with my existing CrowdWorks bot?**  
A: No. Existing bot **applies** to jobs. This bot **replies** to proposals/messages from clients.

**Q: How often should I run this?**  
A: 2-3 times per day (morning, afternoon, evening). Avoid excessive checks.

**Q: What if I want to manually respond to some proposals?**  
A: Keep auto-send off. Review generated replies, then manually send via browser or use manual handler.

**Q: Can I customize the reply style?**  
A: Yes! Edit `generate_reply()` function in the script or ask me to adjust it.

**Q: What if a proposal needs clarification before responding?**  
A: Keep auto-send off for those. Review the reply, decide if it needs more info, then respond manually.

---

**Ready to test?**

```bash
# 1. Add credentials to .env
# 2. Run in review mode first
python crowdworks_auto_handler.py --visible

# 3. Check generated replies
dir crowdworks_reply_*.txt

# 4. Enable auto-send when confident
# Edit .env: CROWDWORKS_AUTO_SEND=true
```

🚀
