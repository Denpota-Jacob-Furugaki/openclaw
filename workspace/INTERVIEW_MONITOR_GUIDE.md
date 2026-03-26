# Interview Request Monitor - Usage Guide

Two versions available for monitoring interview/meeting requests:

## 🚀 Enhanced Version (Recommended)

**File:** `check_interview_with_links.py`

**What it does:**
- ✅ Scans Gmail for interview/meeting keywords
- ✅ **Extracts links** from emails (CrowdWorks, Lancers, LinkedIn, etc.)
- ✅ **Follows links** and scrapes full content
- ✅ Takes screenshots of linked pages
- ✅ Provides complete context for decision-making

**Supported Platforms:**
- CrowdWorks (crowdworks.jp)
- Lancers (lancers.jp)
- Coconala (coconala.com)
- Workship (workship.jp)
- Forkwell (forkwell.com)
- Findy (findy-code.io)
- LinkedIn (linkedin.com)
- Wantedly (wantedly.com)
- Green-Japan (green-japan.com)
- BizReach (bizreach.jp)

**Usage:**
```bash
cd C:\Users\denpo\.openclaw\workspace
python check_interview_with_links.py
```

**Requirements:**
- `google_token.json` (Gmail OAuth)
- `playwright` installed: `pip install playwright`
- Playwright browsers: `playwright install chromium`

**Output:**
```
🎯 **1 Interview/Meeting Request Found!**

**1. CrowdWorks - プロジェクト提案依頼**
   From: noreply@crowdworks.jp
   Date: Tue, 24 Mar 2026 10:00:00
   Keywords: 提案, メッセージ, 応募

   📧 Email: クライアントから提案依頼が届いています...

   🔗 Links found: 1
      • https://crowdworks.jp/public/jobs/12345

   📄 **Webアプリ開発のお仕事**
      Client: テック株式会社
      ReactとNode.jsを使用したWebアプリケーションの開発案件です...
      Screenshot: interview_link_20260324_100000.png

---

📧 Check Gmail: https://mail.google.com/mail/u/0/#inbox
```

**Advantages:**
- See full job details without opening Gmail
- Screenshots saved for later review
- Extracts client info, budget, timeline from platform pages
- Better context for quick decisions

**Disadvantages:**
- Slower (needs to scrape pages)
- Requires Playwright setup
- May fail if pages need login

---

## ⚡ Lightweight Version

**File:** `check_interview_requests.py`

**What it does:**
- ✅ Scans Gmail for interview/meeting keywords
- ✅ Shows email preview and sender
- ❌ Does NOT follow links

**Usage:**
```bash
cd C:\Users\denpo\.openclaw\workspace
python check_interview_requests.py
```

**Requirements:**
- `google_token.json` (Gmail OAuth only)

**Output:**
```
🎯 **1 Interview/Meeting Request Found!**

**1. CrowdWorks - プロジェクト提案依頼**
   From: noreply@crowdworks.jp
   Date: Tue, 24 Mar 2026 10:00:00
   Keywords: 提案, メッセージ
   Preview: クライアントから提案依頼が届いています。以下のリンクから確認してください...

📧 Check Gmail: https://mail.google.com/mail/u/0/#inbox
```

**Advantages:**
- Fast (no browser automation)
- Fewer dependencies
- Always works

**Disadvantages:**
- Must manually open links to see details
- Less context for decision-making

---

## 🤖 Automatic Monitoring (Heartbeat)

Both scripts can run automatically via OpenClaw heartbeat.

**Current configuration** (in `HEARTBEAT.md`):
- Morning check: 9:00-10:00
- Afternoon check: 14:00-15:00
- Evening check: 18:00-19:00
- Silent hours: 23:00-08:00

**Which version runs:**
- If Playwright available → Enhanced version
- If Playwright missing → Lightweight version (fallback)

---

## 🔧 Setup

### 1. Gmail OAuth (Required for both)

See `GMAIL_BOT_SETUP.md` for detailed instructions.

Quick version:
1. Enable Gmail API in Google Cloud Console
2. Create OAuth credentials (Desktop app)
3. Download as `google_credentials.json`
4. Run any Gmail script to authenticate (saves `google_token.json`)

### 2. Playwright (Required for Enhanced version only)

```bash
# Install Playwright
pip install playwright

# Install browser
playwright install chromium
```

**If you skip this step:** Heartbeat will use lightweight version instead.

---

## 📊 What Gets Saved

Both scripts save results to:
- `last_interview_check.json` - Full check results (JSON)

Enhanced version also creates:
- `interview_link_YYYYMMDD_HHMMSS.png` - Screenshots of linked pages

---

## 🎯 Keywords Detected

**English:**
- interview, meet, meeting, schedule
- zoom, google meet, teams, skype, call
- available, availability

**Japanese:**
- 面接, 面談, カジュアル面談, オンライン面談
- ご都合, 日程, 面接日程, 面談希望
- 応募, 提案, メッセージ, 返信

**Platform-specific:**
- proposal (CrowdWorks/Lancers)
- message (LinkedIn/Wantedly)

---

## 🔍 How Link Following Works

1. **Email parsed** → Extract all http/https URLs
2. **Filter** → Keep only job platform URLs
3. **Visit page** → Open in headless browser
4. **Extract content** → Platform-specific selectors
5. **Screenshot** → Save visual reference
6. **Return** → All content to alert

**Platforms with custom extractors:**
- CrowdWorks → Title, description, client name
- Lancers → Project details, budget

**Other platforms:**
- Generic extraction (h1, main content)

---

## 💡 Tips

### For Manual Checking

**Check all unread interview requests:**
```bash
python check_interview_with_links.py
```

**Quick check (lightweight):**
```bash
python check_interview_requests.py
```

### For Automatic Monitoring

**Test heartbeat manually:**
```bash
# In this chat, I'll run the check when heartbeat triggers
# You can also force a check by asking:
# "Check for interview requests now"
```

### For Troubleshooting

**If link scraping fails:**
1. Check screenshot file to see what loaded
2. Try opening link manually
3. Page may require login (use lightweight version instead)

**If no alerts despite having emails:**
1. Check keywords match (`last_interview_check.json`)
2. Verify emails are unread
3. Check date filter (only last 7 days)

---

## 🚨 When to Use Which Version

| Scenario | Use |
|----------|-----|
| CrowdWorks/Lancers proposal | **Enhanced** - Get full job details |
| LinkedIn recruiter message | **Enhanced** - See full context |
| Email with Zoom link only | Lightweight - No platform page to scrape |
| Quick daily check | Lightweight - Faster |
| Deep investigation | **Enhanced** - Full context + screenshots |

---

## 🔄 Switching Versions

Edit `HEARTBEAT.md` to change which script runs:

```markdown
# For enhanced (default):
Script: `check_interview_with_links.py`

# For lightweight:
Script: `check_interview_requests.py`
```

Or I can automatically detect:
- Try enhanced first
- Fallback to lightweight if Playwright missing

---

## ❓ FAQ

**Q: Will this work for platforms not in the list?**  
A: Yes! The generic extractor works for any URL. Add specific extractors for better results.

**Q: What if a page requires login?**  
A: Enhanced version will fail gracefully. You'll still see the email preview and link.

**Q: Can I add more platforms?**  
A: Yes! Edit `JOB_PLATFORMS` list in the script. Add custom selectors for better extraction.

**Q: How do I stop monitoring?**  
A: Clear `HEARTBEAT.md` or remove the interview check task.

---

**Ready to use!** Run the enhanced version now to test, or wait for the next heartbeat check. 🚀
