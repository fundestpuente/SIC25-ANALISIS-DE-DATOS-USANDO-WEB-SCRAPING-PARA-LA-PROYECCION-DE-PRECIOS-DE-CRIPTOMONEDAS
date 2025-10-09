# Scheduler

- Script: `scheduler/scheduler.py`
- Behavior: fetches sources from `/api/scraping/sources` and schedules POST to `/api/scraping/run?source=<name>` every 2 minutes.
- Logging: writes to `scheduler.log` (in the current working directory).
