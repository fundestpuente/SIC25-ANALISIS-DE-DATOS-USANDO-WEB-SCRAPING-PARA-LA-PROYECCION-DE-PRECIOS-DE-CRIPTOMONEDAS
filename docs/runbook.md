# Runbook (from repository files)

## Backend (FastAPI)
- **Requirements:** `backscrap/requirements.txt`
- **Entrypoint:** `backscrap/run.py`
- **Bind:** host `0.0.0.0`, port `9000`
- **Docs:** `http://localhost:9000/docs`

## Scheduler
- **Script:** `scheduler/scheduler.py`
- **Interval:** every **2 minutes** per source
- **Flow:**
  1. GET `/api/scraping/sources`
  2. POST `/api/scraping/run?source=<name>`

## Observatory (Streamlit)
- **Requirements:** `observatory/requirements.txt`
- **Script:** `observatory/app.py`
- **API URL (as coded):** `http://localhost:9000/api/scraping/results`
