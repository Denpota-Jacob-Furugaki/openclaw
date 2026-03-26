# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Job Search Tools

### Gmail Auto-Reply Bot

**Location:** `C:\Users\denpo\.openclaw\workspace\gmail_job_reply_bot.py`  
**Setup Guide:** `GMAIL_BOT_SETUP.md`  
**Status:** Ready to use (needs Google OAuth setup first)

**Quick Start:**
```bash
cd C:\Users\denpo\.openclaw\workspace
python gmail_job_reply_bot.py
```

**Features:**
- Monitors job platform emails (LinkedIn, Indeed, Wantedly, etc.)
- AI evaluation of fit (remote + software/AI/DX roles)
- Creates draft replies (safe mode) or auto-sends
- Tracks processed emails to avoid duplicates

**Config:**
- Mode: **DRAFT** (review before sending)
- Platforms monitored: LinkedIn, Indeed, Wantedly, Green-Japan, BizReach, Doda, Rikunabi, MyNavi, Findy, Forkwell, LevTech, Geekly, Paiza, CrowdWorks, Lancers
- Auto-declines: non-remote roles, non-tech positions

### Interview Alert Monitor

**Location:** `C:\Users\denpo\.openclaw\workspace\check_interview_requests.py`  
**Status:** Active (runs via heartbeat)

**Quick Start:**
```bash
cd C:\Users\denpo\.openclaw\workspace
python check_interview_requests.py
```

**Features:**
- Scans unread emails for interview/meeting requests
- Keywords: interview, 面接, 面談, meet, schedule, zoom, teams, etc.
- Alerts immediately when found
- Shows sender, subject, preview

**Monitoring:**
- Automatic checks: morning (9-10), afternoon (14-15), evening (18-19)
- Silent hours: 23:00-08:00 (urgent only)
- Configured in: `HEARTBEAT.md`

### Reply Templates

**Location:** `job_reply_templates.md`

Pre-written templates for quick manual replies:
- ✅ Interested (Japanese) - Remote confirmed
- ✅ Interested (Japanese) - Asking about remote
- ✅ Interested (English)
- 🔴 Decline (Japanese/English)

**Usage:** Copy template → customize → send

### Existing Job Bots (from CascadeProjects)

**Location:** `C:\Users\denpo\CascadeProjects\my-first-ai-agent\`

- `daijob_auto_reply.py` - Daijob scout messages
- `crowdworks_bot.py` - CrowdWorks proposals
- `lancers_bot.py` - Lancers projects
- `forkwell_bot.py` - Forkwell job applications
- `linkedin_bot.py` - LinkedIn Easy Apply
- `findy_bot.py` - Findy job applications

All use Playwright for browser automation + OpenAI for evaluation/replies.

## Examples

```markdown
### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
