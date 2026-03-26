# Heartbeat — Salesman Job Hunt Tasks

## 🎯 Mission: Get Denpo Hired

Active until Denpo confirms a solid position. Run these checks on every heartbeat.

---

## 🔴 IMMEDIATE (every heartbeat)

Check for interview / meeting requests:
```
cd C:\Users\denpo\.openclaw\workspace
python check_interview_requests.py
```
If found → alert Denpo immediately. Do NOT wait for next cycle.

---

## ⏰ SCHEDULED TASKS

### Morning (9:00–10:00 JST)
- Run full platform scan + apply to new matches:
  ```
  cd C:\Users\denpo\.openclaw\workspace
  python continuous_job_hunter.py
  ```
- Run Gmail reply bot:
  ```
  python gmail_job_reply_bot.py
  ```
- Send morning summary to Denpo

### Afternoon (14:00–15:00 JST)
- Run platform scan again
- Check for new recruiter replies
- Send afternoon summary

### Evening (18:00–19:00 JST)
- Interview request check
- Send daily stats summary:
  - Applications sent today
  - Replies received
  - Interviews pending
  - Any blockers

---

## 📊 TRACKING

State file: `C:\Users\denpo\.openclaw\workspace\job_hunt_stats.json`

After each run, update `job_state.json` in this workspace with:
```json
{
  "lastChecks": {
    "interviewMonitor": "<unix timestamp>",
    "fullScan": "<unix timestamp>",
    "gmailBot": "<unix timestamp>"
  },
  "todayStats": {
    "applicationsRun": 0,
    "interviewRequests": 0,
    "repliesSent": 0
  }
}
```

---

## 🚨 KNOWN ISSUES

- Google Sheets API returning HTTP 500 errors (as of 2026-03-24) — log error, skip sheets update, continue other tasks
- CrowdWorks login failures — check screenshot logs in main workspace

---

## ✅ STOP CONDITION

When Denpo says he's accepted a job offer:
1. Disable all cron jobs for this agent
2. Send final stats summary
3. Update `job_state.json` with `"status": "hired"`
4. Replace this file with `# Heartbeat - DISABLED`
