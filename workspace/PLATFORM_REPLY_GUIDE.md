# Platform Message Reply System - Complete Guide

Automatically read and reply to messages on job platforms (CrowdWorks, Lancers, etc.)

## 🎯 What This Does

1. ✅ **Authenticates** to job platforms (saves session cookies)
2. ✅ **Navigates** to proposal/message pages
3. ✅ **Reads** full message content (job details, client info, budget)
4. ✅ **Takes screenshots** for reference
5. ✅ **Generates AI replies** in your style
6. ✅ **Sends replies** directly on the platform

## 🚀 Quick Start

### Setup Credentials

Add to your `.env` file:

```bash
# CrowdWorks
CROWDWORKS_EMAIL=your-email@example.com
CROWDWORKS_PASSWORD=your-password

# Lancers
LANCERS_EMAIL=your-email@example.com
LANCERS_PASSWORD=your-password

# Forkwell (optional)
FORKWELL_EMAIL=your-email@example.com
FORKWELL_PASSWORD=your-password
```

### Install Dependencies

```bash
pip install playwright python-dotenv openai
playwright install chromium
```

### Basic Usage

**Read message and generate reply (review before sending):**
```bash
cd C:\Users\denpo\.openclaw\workspace
python platform_message_handler.py https://crowdworks.jp/proposals/288200154
```

**Auto-reply (send immediately):**
```bash
python platform_message_handler.py https://crowdworks.jp/proposals/288200154 --auto-reply
```

**Generate decline message:**
```bash
python platform_message_handler.py https://crowdworks.jp/proposals/288200154 --decline
```

**Show browser (not headless):**
```bash
python platform_message_handler.py https://crowdworks.jp/proposals/288200154 --visible
```

## 📋 Example Output

```
🔍 Logging into CrowdWorks...
✓ Logged into CrowdWorks
📄 Navigating to https://crowdworks.jp/proposals/288200154
📸 Screenshot saved: crowdworks_message_20260324_142600.png
📝 Extracted: Webアプリ開発のお仕事... (3 messages)

=== Generated Reply ===
ご連絡いただきありがとうございます。

ReactとNode.jsを使用したWebアプリ開発案件に大変興味がございます。
私はフルスタック開発を専門としており、React/Next.js、Node.jsの実装経験が豊富です。

リモート勤務での対応は可能でしょうか？
可能であれば、詳細についてお話しできればと思います。

ポートフォリオ：https://denpota-portfolio.vercel.app/

よろしくお願いいたします。
古垣 伝法太
=======================

Auto-reply disabled. Review the reply above and send manually.
Result saved to message_handled_20260324_142600.json

✓ Message processed
Title: ReactとNode.jsを使用したWebアプリ開発
Client: テック株式会社

Generated reply:
ご連絡いただきありがとうございます。...

Reply sent: False
Screenshot: crowdworks_message_20260324_142600.png
```

## 🎮 Integration with Interview Monitor

The interview monitor now suggests how to handle found messages:

```bash
# 1. Check for interview requests
python check_interview_with_links.py

# Output shows:
🎯 **1 Interview/Meeting Request Found!**
...
💡 To read and reply to these messages on the platform:
   python platform_message_handler.py https://crowdworks.jp/proposals/288200154
   python platform_message_handler.py https://crowdworks.jp/proposals/288200154 --auto-reply

# 2. Handle the message
python platform_message_handler.py https://crowdworks.jp/proposals/288200154
```

## 🤖 Workflow Options

### Conservative (Recommended for First Use)

1. **Check emails** → `python check_interview_with_links.py`
2. **Read message** → `python platform_message_handler.py <url>`
3. **Review generated reply**
4. **Manually send** if good, or edit and send via browser

### Semi-Automated

1. **Check emails** → automated via heartbeat
2. **Get alert** with links
3. **Run handler** → `python platform_message_handler.py <url>`
4. **Review reply**
5. **Send manually** or re-run with `--auto-reply`

### Fully Automated (After Testing)

1. **Check emails** → automated
2. **Handle messages** → automated with `--auto-reply`
3. **Monitor logs** → review what was sent

## 🔧 Supported Platforms

### CrowdWorks ✅
- **Authentication:** Email/password
- **Reads:** Job title, description, client name, budget, messages
- **Replies:** Via message textarea + send button
- **Status:** Fully implemented

### Lancers ✅
- **Authentication:** Email/password
- **Reads:** Job title, description
- **Replies:** Via textarea + send button
- **Status:** Fully implemented

### Forkwell 🔶
- **Authentication:** Email/password
- **Status:** Login implemented, message handling TODO

### LinkedIn, Wantedly, etc. 🔷
- **Status:** Can be added (similar structure)

## 📸 What Gets Saved

**Per message handled:**
- `<platform>_message_YYYYMMDD_HHMMSS.png` - Full page screenshot
- `<platform>_sent_YYYYMMDD_HHMMSS.png` - Confirmation screenshot
- `message_handled_YYYYMMDD_HHMMSS.json` - Full data (title, client, reply, etc.)
- `platform_messages.log` - Activity log

**Session cookies:**
- `platform_sessions/crowdworks_session.json` - Reusable login session
- `platform_sessions/lancers_session.json` - Reusable login session

## 🔐 Security

**Session persistence:**
- Login credentials stored in `.env` (gitignored)
- Session cookies saved locally (avoid repeated logins)
- Sessions expire after ~30 days (auto re-login)

**Never store in code:**
- Passwords
- API keys
- Session tokens

**Keep `.env` safe:**
- Add to `.gitignore`
- Never commit to public repos
- Backup securely

## 🛠️ Troubleshooting

### "Credentials not found in .env"

Add credentials to `.env` file:
```bash
CROWDWORKS_EMAIL=your-email
CROWDWORKS_PASSWORD=your-password
```

### "Login failed"

1. Check credentials are correct
2. Try logging in manually in browser first
3. Delete session file: `rm platform_sessions/crowdworks_session.json`
4. Run with `--visible` to see what's happening

### "Could not find message textarea"

1. Check screenshot to see page state
2. Platform may have changed selectors
3. Update selectors in `platform_message_handler.py`
4. Report to me for fix

### "Reply not sent"

1. Check `platform_messages.log` for errors
2. Run with `--visible` to debug
3. May need to update send button selector

## 📊 AI Reply Generation

**What it considers:**
- Job title and description
- Client name
- Budget
- Previous messages in thread
- Your profile (skills, achievements)
- Remote work preference

**Reply style:**
- Polite and professional
- Highlights 1-2 relevant skills
- Asks about remote work if not mentioned
- Requests next steps (interview/call)
- Under 200 characters (Japanese)

**Decline style:**
- Brief thank you
- Polite decline
- 2-3 sentences
- No long explanations

## 💡 Advanced Usage

### Batch Processing

```bash
# Process multiple URLs
for url in \
  "https://crowdworks.jp/proposals/111111" \
  "https://crowdworks.jp/proposals/222222" \
  "https://crowdworks.jp/proposals/333333"
do
  python platform_message_handler.py "$url"
done
```

### Custom Reply

```python
# Edit platform_message_handler.py
# Modify generate_reply() function
# Add custom logic for specific clients/projects
```

### Add New Platform

```python
# In platform_message_handler.py

class NewPlatformHandler(PlatformHandler):
    def __init__(self):
        super().__init__('newplatform')
    
    def login(self):
        # Implement login
        pass
    
    def read_message(self, url):
        # Extract message data
        pass
    
    def send_reply(self, message_text):
        # Send reply
        pass
```

## 🔄 Integration with Existing Bots

You already have job application bots. This complements them:

**Existing bots (in CascadeProjects):**
- `daijob_auto_reply.py` - Daijob scout messages
- `crowdworks_bot.py` - CrowdWorks auto-apply
- `lancers_bot.py` - Lancers auto-apply

**New system:**
- Handles **replies to proposals** (not applications)
- Works with **email notifications** → follow link → reply
- More interactive (reads client messages, generates context-aware replies)

**Use together:**
1. Existing bot finds and applies to jobs
2. Client responds to your application
3. Email notification arrives
4. Interview monitor detects it
5. **This system reads and replies** on the platform

## 📈 Next Steps

1. **Test with one URL** (no --auto-reply first)
2. **Review generated reply** quality
3. **Adjust profile** in `PROFILE_SUMMARY` if needed
4. **Enable auto-reply** for trusted platforms
5. **Integrate with heartbeat** for full automation

## ❓ FAQ

**Q: Will this work if I'm already logged in on my browser?**  
A: Yes, but it uses separate session. Won't interfere with your manual browsing.

**Q: Can I use this for platforms not listed?**  
A: Yes, but you'll need to implement a handler class. I can help!

**Q: What if I want to edit the reply before sending?**  
A: Don't use `--auto-reply`. Review the generated reply, then either:
- Send manually via browser
- Edit the script and re-run with `--auto-reply`

**Q: How do I stop auto-replying?**  
A: Don't use `--auto-reply` flag. Always review first by default.

**Q: Can this handle attachments?**  
A: Not yet. Currently text-only replies. Can be added if needed.

---

**Ready to test?** Try with a real CrowdWorks URL:

```bash
# 1. Add credentials to .env
# 2. Run the handler
python platform_message_handler.py https://crowdworks.jp/proposals/YOUR_PROPOSAL_ID

# 3. Review the generated reply
# 4. If good, re-run with --auto-reply
python platform_message_handler.py https://crowdworks.jp/proposals/YOUR_PROPOSAL_ID --auto-reply
```

🚀
