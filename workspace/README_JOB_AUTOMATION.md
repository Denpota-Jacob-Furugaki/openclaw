# Job Search Automation - Quick Reference

Your AI assistant is now set up to help with job search email replies!

## 📁 Files Created

1. **`gmail_job_reply_bot.py`** - Automated email reply bot for Gmail
2. **`check_interview_with_links.py`** - Enhanced interview monitor (follows links)
3. **`check_interview_requests.py`** - Lightweight interview monitor (email only)
4. **`platform_message_handler.py`** - Reply to specific platform URLs (CrowdWorks, Lancers)
5. **`crowdworks_auto_handler.py`** - 🆕 **Automatic CrowdWorks proposal handler** (batch processing)
6. **`job_reply_templates.md`** - Pre-written reply templates (Japanese/English)
7. **`GMAIL_BOT_SETUP.md`** - Detailed setup instructions
8. **`PLATFORM_REPLY_GUIDE.md`** - Guide to replying on platforms
9. **`CROWDWORKS_AUTO_SETUP.md`** - 🆕 **CrowdWorks auto-handler guide**
10. **`INTERVIEW_MONITOR_GUIDE.md`** - Interview monitoring guide
11. **`USER.md`** (updated) - Your profile and job preferences
12. **`TOOLS.md`** (updated) - References to job search tools
13. **`HEARTBEAT.md`** (updated) - Proactive monitoring tasks
14. **`.env.example`** - Environment variables template

## 🚀 Quick Start

### Option 1: Full Automation (Gmail → Platform Reply)

**Complete workflow:**
1. Monitor Gmail for job/interview emails
2. Follow links to platforms (CrowdWorks, Lancers, etc.)
3. Read full message on platform
4. Generate AI reply in your style
5. Send reply directly on platform

**Setup:**
```bash
# See GMAIL_BOT_SETUP.md + PLATFORM_REPLY_GUIDE.md
cd C:\Users\denpo\.openclaw\workspace

# 1. Check for interview requests (finds CrowdWorks links)
python check_interview_with_links.py

# 2. Handle platform message (reads + replies)
python platform_message_handler.py https://crowdworks.jp/proposals/288200154

# 3. Auto-send (after testing)
python platform_message_handler.py https://crowdworks.jp/proposals/288200154 --auto-reply
```

### Option 2: Gmail Replies Only (Automated Bot)

**What it does:**
- Monitors unread emails from job platforms (LinkedIn, Indeed, Wantedly, etc.)
- AI evaluates if job matches your criteria (remote + software/AI/DX)
- Creates draft replies automatically (or auto-sends if configured)

**Setup:**
```bash
# See GMAIL_BOT_SETUP.md for full instructions
cd C:\Users\denpo\.openclaw\workspace

# 1. Get Google OAuth credentials from Cloud Console
# 2. Save as google_credentials.json
# 3. Run bot (will authenticate first time)
python gmail_job_reply_bot.py

# 4. Check Gmail → Drafts for generated replies
```

**Daily automation:** Schedule with Windows Task Scheduler or OpenClaw cron (see setup guide).

### Option 2: Manual with Templates

**What it does:**
- You forward job emails to this chat
- I analyze and generate personalized replies using templates
- You review and send

**Usage:**
1. Forward job email to me
2. I'll tell you if it's a good fit
3. I'll provide a customized reply to copy/paste
4. You review and send via Gmail

**Templates available in:** `job_reply_templates.md`

## 🎯 Interview Alert System

**NEW!** I'll now proactively monitor your Gmail and alert you when interview/meeting requests arrive.

**What triggers an alert:**
- Keywords: "interview", "面接", "面談", "meet", "schedule", "zoom", "google meet", "teams", "応募", "提案"
- From: recruiters, job platforms, company HR
- Status: unread emails from last 7 days

**How it works:**
1. Heartbeat checks run periodically (morning, afternoon, evening)
2. If interview request found → **follows links** to extract full details
3. Scrapes content from CrowdWorks, Lancers, LinkedIn, etc.
4. Takes screenshots for reference
5. Alerts with complete context

**Two versions available:**
- **Enhanced** (`check_interview_with_links.py`) - Follows links, scrapes content, takes screenshots
- **Lightweight** (`check_interview_requests.py`) - Email preview only (faster)

**Manual check anytime:**
```bash
# Enhanced version (recommended)
cd C:\Users\denpo\.openclaw\workspace
python check_interview_with_links.py

# Or lightweight version
python check_interview_requests.py
```

**What you'll see in alerts:**
- 📧 Sender name and email
- 📋 Subject line
- 🔑 Keywords detected
- 📄 Email preview
- 🔗 **Links found in email**
- 📑 **Full content from linked pages** (job details, client info, budget)
- 📸 **Screenshots** of platform pages
- 🔗 Direct link to Gmail

**See full guide:** `INTERVIEW_MONITOR_GUIDE.md`

## 🎯 Your Job Search Criteria

### ✅ Interested In:
- Software Engineering / Developer roles
- AI Development / Machine Learning
- Full-stack Development (JavaScript/TypeScript, React, Node, Python)
- DX / Digital Transformation
- Marketing Engineering (dev + marketing hybrid)
- **MUST be remote or mostly remote**

### ❌ NOT Interested In:
- Pure sales / 営業
- Admin / clerical / 事務
- Manual labor / construction / delivery
- Customer service / call center
- Hospitality / restaurant
- Non-tech roles

## 📝 Reply Style

**When Interested:**
- Thank recruiter
- Express strong interest
- Highlight 2-3 relevant achievements
- Ask about remote work (if not clear)
- Request casual interview/call
- Include portfolio link

**When Declining:**
- Brief thank-you (2-3 sentences)
- Polite decline
- No lengthy explanations

**Language:**
- Match recruiter's language (Japanese → Japanese, English → English)
- Japanese: concise (under 200 chars ideal)
- English: under 200 words

## 🔧 Your Profile (for AI replies)

**Denpota Furugaki (古垣 伝法太)**
- Bilingual (Japanese/English), Korean business level
- Tech: JavaScript/TypeScript, React/Next.js, Node.js, Python, AI/ML
- Marketing: Google/META Ads, SEO, analytics
- Key achievements: Onitsuka Tiger ROAS 120%, Meta Q1 Top Performer #1/34
- Portfolio: https://denpota-portfolio.vercel.app/
- Email: denpotafurugaki@gmail.com | Phone: 080-2466-0377

## 💡 How to Use This Chat

### Forward Job Emails

Just paste the email content:
```
From: recruiter@company.com
Subject: Software Engineer (Remote) - Tokyo

Dear Denpota,
We found your profile and...
[full email]
```

I'll respond with:
1. **Evaluation:** Is this a good fit?
2. **Recommended reply:** Customized based on the job
3. **Action:** Copy/paste or let bot handle it

### Ask for Custom Replies

```
"Draft a reply for this engineering role at [Company X]"
"Decline this sales position politely"
"Generate interest reply asking about remote work"
```

### Check Bot Status

```
"Show me what emails the bot processed today"
"Read gmail_job_bot.log"
```

## 📊 Monitoring

**Bot logs everything:**
```bash
# View recent activity
cat gmail_job_bot.log

# Summary stats shown after each run:
# - Processed: X
# - Interested: Y
# - Declined: Z
# - Mode: DRAFT/AUTO-SEND
```

**Processed emails tracked in:** `gmail_processed.json`

## 🛡️ Safety Features

1. **Draft mode by default** - Bot creates drafts, doesn't send
2. **No duplicates** - Tracks processed emails
3. **Remote work filter** - Auto-declines non-remote roles
4. **Full logging** - Audit trail of all actions
5. **You review** - Check drafts before sending

## 🔄 Workflow Options

### Conservative (Recommended)
1. Bot creates drafts
2. You review in Gmail
3. Edit if needed
4. Send manually

### Semi-Automated
1. Bot creates drafts
2. You check daily summary
3. Send all good drafts at once

### Fully Automated (After Testing)
1. Enable `AUTO_SEND = True` in bot
2. Bot sends replies automatically
3. You monitor logs

## 📚 Reference Files

| File | Purpose |
|------|---------|
| `gmail_job_reply_bot.py` | Main automation bot |
| `GMAIL_BOT_SETUP.md` | Setup instructions |
| `job_reply_templates.md` | Manual reply templates |
| `USER.md` | Your profile & preferences |
| `TOOLS.md` | Tool reference |
| `gmail_job_bot.log` | Bot activity log |
| `gmail_processed.json` | Processed email tracker |

## 🎓 Learning Resources

**Your existing bots:**
- Daijob bot: `C:\Users\denpo\CascadeProjects\my-first-ai-agent\daijob_auto_reply.py`
- Similar patterns for CrowdWorks, Lancers, Forkwell, LinkedIn, Findy

**Gmail API Docs:**
- https://developers.google.com/gmail/api

**OpenAI API (for AI evaluation):**
- https://platform.openai.com/docs

## ❓ Common Questions

**Q: Can I use this for other job platforms besides Gmail?**  
A: Yes! Your existing bots handle Daijob, CrowdWorks, Lancers, etc. directly via Playwright. This Gmail bot catches platforms that email you (LinkedIn, Indeed, Wantedly).

**Q: What if I want to reply differently to a specific company?**  
A: Just tell me! I'll generate a custom reply. Or edit the bot's evaluation logic to recognize specific companies.

**Q: How do I stop processing old emails?**  
A: The bot only processes unread emails. Mark old ones as read, or delete `gmail_processed.json` to reset.

**Q: Can I schedule this to run daily?**  
A: Yes! See `GMAIL_BOT_SETUP.md` for Windows Task Scheduler or OpenClaw cron setup.

## 🚨 Need Help?

Just ask me:
- "Check the bot logs"
- "Why did the bot decline [company]?"
- "Generate a custom reply for [email]"
- "Update my job preferences"

---

**Ready to go!** Forward me a job email or set up the bot to see it in action. 🚀
