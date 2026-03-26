# Heartbeat — Cron

On every heartbeat:

1. Read `CRONTAB.md` and `cron_state.json`
2. Check the current time (JST) against each job's schedule
3. Run any job that is overdue
4. Update `cron_state.json` after each run
5. Alert Denpo on any failure

## Logic

For time-based jobs: compare `lastRun` timestamp to schedule.
- If `lastRun` is null → treat as overdue, run now
- If current time >= scheduled time and `lastRun` is before today's scheduled time → run

For interval jobs (e.g. every 60 min):
- If `lastRun` is null OR `(now - lastRun) >= interval` → run

## After All Jobs

If all jobs passed: `HEARTBEAT_OK`
If any job failed or produced an alert: send message to Denpo
