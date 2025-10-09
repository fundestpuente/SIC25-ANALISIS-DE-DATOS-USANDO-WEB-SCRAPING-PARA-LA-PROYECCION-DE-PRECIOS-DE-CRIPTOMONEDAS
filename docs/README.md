# Crypto Scraping Project — Documentation


## Modules
- **backscrap/** — FastAPI backend (routes under the `backscrap/app/controller` package).
- **scheduler/** — Simple task scheduler for triggering scraping jobs via HTTP.
- **observatory/** — Streamlit dashboard to visualize stored snapshots.

## Quick Start

### 1) Backend (FastAPI)
- Install dependencies:
  ```bash
  pip install -r backscrap/requirements.txt
  ```
- Run the API:
  ```bash
  python backscrap/run.py
  ```
- Default bind (discovered in the repo): **host=0.0.0.0**, **port=9000**.
- API docs: `http://localhost:9000/docs`

### 2) Scheduler
- Install dependencies if needed (uses `requests`, `schedule` — typically included in backend requirements or your environment).
- Start:
  ```bash
  python scheduler/scheduler.py
  ```
- Behavior: fetches available sources from the API, then triggers `/api/scraping/run?source=<name>` every **2 minutes**.

### 3) Observatory (Streamlit)
- Install dependencies:
  ```bash
  pip install -r observatory/requirements.txt
  ```
- Launch:
  ```bash
  streamlit run observatory/app.py
  ```
- The dashboard expects the API results endpoint at:
  ```text
  http://localhost:9000/api/scraping/results
  ```

