
# Data Analysis with Web Scraping for Cryptocurrency Price Projection
**Observatory + API + Scheduler**

> Academic project focused on **putting real, verifiable data in users’ hands**—without selling courses, without affiliates, and **without nudging purchases**. The purpose is **trust and transparency**: capture public information from multiple sources, normalize it, and display it clearly so each user can form their own view. _This is not financial advice._

---

## 1) Problem statement (summary)
Public crypto‑market information is often **fragmented**, published in **heterogeneous formats**, and lacks clear **traceability**. This makes basic analysis slow and error‑prone—especially for students and first‑time users.  
Our prototype proposes a **lightweight stack** that automates data ingestion (web scraping), **standardizes** fields, and exposes them through an **API** and a **simple dashboard** to enable quick source‑to‑source comparisons.

---

## 2) Project objectives
- **Automate** periodic collection of public market data (e.g., price, 24h change, 24h volume, market cap, timestamp, source).
- **Standardize** the data model so users can **compare multiple sources** for the same asset.
- **Expose** results through a **REST API** and **visualize** them in an **observatory (dashboard)** for immediate exploratory analysis.
- **Guarantee traceability and transparency** by showing, for every record, the **source, capture time, method, and limitations**.
- **Avoid dark patterns**: the project **does not** nudge purchases, **does not** sell courses, and **does not** include affiliate links.

---

## 3) Tools used
- **Backend (API):** Python + FastAPI; **SSE** (Server‑Sent Events) for real‑time status updates.
- **Scraping & processing:** Playwright (navigation/collection), Pandas (cleaning/transformation).
- **Storage:** MongoDB (via `motor` async driver and managers in the repo).
- **Observatory (dashboard):** Streamlit with Plotly/Matplotlib/Seaborn; Requests to consume the API.
- **Task scheduling:** `schedule` (time‑based simple scheduler).
- **Utilities:** Broadcaster / sseclient for event streaming.

> All dependencies and scripts live under `backscrap/`, `scheduler/`, and `observatory/` (see their `requirements.txt`).

---

## 4) Installation & Getting Started

### 4.1 Prerequisites
- **Python 3.10+**
- **MongoDB** running locally or remotely (you’ll need a URI and database name)
- **Playwright browsers** (we install them below)

### 4.2 Clone and create a virtual environment
```bash
cd SIC25-ANALISIS-DE-DATOS-USANDO-WEB-SCRAPING-PARA-LA-PROYECCION-DE-PRECIOS-DE-CRIPTOMONEDAS

# Create & activate a virtualenv (Linux/macOS)
python -m venv .venv && source .venv/bin/activate
# On Windows (PowerShell)
# python -m venv .venv ; .\.venv\Scripts\Activate.ps1
```

### 4.3 Install dependencies
> The repository includes per‑module `requirements.txt`. Install each component exactly as declared and add the runtime libs used in code.

**Backend (API)**
```bash
pip install fastapi uvicorn motor pymongo playwright pandas sse-starlette broadcaster sseclient schedule
# Install Playwright browsers
python -m playwright install
```

**Observatory (dashboard)**
```bash
pip install -r observatory/requirements.txt
```

**Scheduler**
```bash
pip install requests schedule
```

### 4.4 Configure environment variables (API)
The API requires these variables (see `backscrap/app/utils/config.py`):
```bash
export MONGO_DATABASE_URL="mongodb://localhost:27017"
export MONGO_DATABASE_NAME="CriptoScrapping"
# Optional
export DEV_MODE=true
# On Windows (PowerShell):
# $env:MONGO_DATABASE_URL = "mongodb://localhost:27017"
# $env:MONGO_DATABASE_NAME = "CriptoScrapping"
# $env:DEV_MODE = "true"
```

### 4.5 Run the services

**Terminal A — Start the API**
```bash
python backscrap/run.py
# Serves at http://localhost:9000
# Interactive docs: http://localhost:9000/docs
```

**Terminal B — Start the Scheduler**
```bash
python scheduler/scheduler.py
# It will discover sources and POST /api/scraping/run?source=<name> every 2 minutes.
# Logs go to scheduler.log
```

**Terminal C — Start the Observatory (dashboard)**
```bash
streamlit run observatory/app.py
# Streamlit will show a local URL (typically http://localhost:8501)
```

### 4.6 See it working
1. Open **Swagger UI** at `http://localhost:9000/docs` and try:
   - `GET  /api/scraping/sources` — list sources
   - `POST /api/scraping/run?source=<name>` — trigger a scrape
   - `GET  /api/scraping/results?source=<name>` — fetch stored snapshots
2. Watch **live status** via SSE:
   - `GET  /api/events/status-stream`
3. Visit the **dashboard** (Streamlit URL printed in Terminal C). You should see tables and charts updating as new snapshots arrive.

### 4.7 Health & quick checks
- API health: `http://localhost:9000/health`
- Mongo connection prints on startup (from `config.py`); ensure the URI/DB are correct.

### 4.8 Troubleshooting
- **Playwright not installed** → run `python -m playwright install`.
- **Mongo errors** → verify `MONGO_DATABASE_URL` and `MONGO_DATABASE_NAME`; ensure the DB is reachable.
- **CORS issues** when opening the dashboard → CORS is permissive by default; check that the API runs on `http://localhost:9000`.
- **Scheduler cannot reach the API** → update `API_BASE_URL` in `scheduler/scheduler.py` if you changed host/port.

---

## 5) What the prototype delivers (result, short)
A working trio—**FastAPI service**, **time‑based scheduler**, and **Streamlit dashboard**—that **automates collection**, **standardizes fields**, and **visualizes** crypto‑market snapshots **with full provenance** (source, timestamp, and caveats). It is **transparency‑first** and **extensible**: new sources and views can be added with minimal changes.

---

### Repository structure (short view)
```
backscrap/     # FastAPI service (controllers, services, repository, utils, run.py)
scheduler/     # Time-based job runner that periodically calls the API
observatory/   # Streamlit dashboard for exploratory analysis
docs/          # Extended documentation (quick start, runbook, SSE events, etc.)
```

<<<<<<< Updated upstream
---
=======
### Responsible‑use note
This project **does not provide investment recommendations** and does not promote buying cryptocurrencies. It is strictly **educational** and **data‑literacy oriented**: it helps users access **traceable and understandable** public information so they can **evaluate it on their own**.
>>>>>>> Stashed changes
