# CRONTAB.md — Job Schedule

All scheduled jobs for Cron to execute.

Format:
```
## [job-id]
- **Schedule:** cron expression or plain description
- **Command:** shell command to run
- **On failure:** what to do
- **Alert:** when to notify Denpo
```

---

## job-hunt-morning
- **Schedule:** Daily at 09:00 JST
- **Command:** `cd C:\Users\denpo\.openclaw\workspace && python continuous_job_hunter.py`
- **On failure:** Log error, alert Denpo, skip to next job
- **Alert:** Always (success summary + any failures)

## job-hunt-afternoon
- **Schedule:** Daily at 14:00 JST
- **Command:** `cd C:\Users\denpo\.openclaw\workspace && python continuous_job_hunter.py`
- **On failure:** Log error, alert Denpo
- **Alert:** On failure only (success is routine)

## gmail-reply-bot-morning
- **Schedule:** Daily at 09:05 JST
- **Command:** `cd C:\Users\denpo\.openclaw\workspace && python gmail_job_reply_bot.py`
- **On failure:** Log error, alert Denpo
- **Alert:** On failure or when interview-related keywords found in output

## gmail-reply-bot-afternoon
- **Schedule:** Daily at 14:05 JST
- **Command:** `cd C:\Users\denpo\.openclaw\workspace && python gmail_job_reply_bot.py`
- **On failure:** Log error, alert Denpo
- **Alert:** On failure or when interview-related keywords found

## interview-monitor
- **Schedule:** Every 60 minutes
- **Command:** `cd C:\Users\denpo\.openclaw\workspace && python check_interview_requests.py`
- **On failure:** Log error, alert Denpo
- **Alert:** IMMEDIATE if interview/meeting request detected

## crowdworks-handler
- **Schedule:** Daily at 09:10 JST and 14:10 JST
- **Command:** `cd C:\Users\denpo\.openclaw\workspace && python crowdworks_auto_handler.py`
- **On failure:** Log error, alert Denpo
- **Alert:** On failure

## daily-digest
- **Schedule:** Daily at 21:00 JST
- **Command:** internal — read job_hunt_stats.json and send summary to Denpo
- **On failure:** Alert Denpo
- **Alert:** Always (this IS the alert)

---

## Adding New Jobs

To add a job, Denpo should send a message like:
> "Add a cron job to run X every Y"

Cron will add the entry here and confirm.

## Pausing / Disabling Jobs

To pause a job, add `- **Status:** PAUSED` to its entry.
Cron will skip paused jobs but keep them in the schedule for easy re-enabling.

## Known Issues

- **Google Sheets API (job-hunt-morning/afternoon):** HTTP 500 errors are intermittent. Log and continue — do not treat as fatal failure.
- **CrowdWorks login failures:** Playwright sessions sometimes fail. Screenshot saved to main workspace. Alert Denpo if 3x consecutive failures.
