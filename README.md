# Crypto Market Scraping & Forecasting — Observatory + API + Scheduler

**A lightweight, production‑minded stack to collect crypto market snapshots from public sources, store them, and explore insights in minutes.**  
This repository ships three focused components that work together out of the box:

- **FastAPI backend** (`backscrap/`) — Orchestrates scraping jobs, persists snapshots, and exposes REST + SSE.
- **Task scheduler** (`scheduler/`) — Triggers scraping at a fixed cadence by calling the API.
- **Streamlit observatory** (`observatory/`) — A clean dashboard to explore market trends, compare sources, and spot opportunities.

> Looking for detailed, step‑by‑step docs? See the `docs/` folder in this repo. It includes API routes, runbooks, and troubleshooting explicitly derived from the codebase.

---

## Why this project

- **Move fast**: Bring data online quickly with a tiny footprint (API + scheduler + dashboard).
- **Stay flexible**: Keep sources decoupled from visualization; plug new scrapers and compare providers.
- **Show value**: Communicate insights clearly (market cap leaders, cross‑source price dispersion, volatility, and more).

---

## Architecture (at a glance)

```
+----------------------------+        POST /api/scraping/run?source=X       +-------------------------+
|  Scheduler (scheduler.py)  |  ──────────────────────────────────────────▶ |  FastAPI (backscrap)    |
+----------------------------+                                             |  REST + SSE + storage   |
                                                                          +-----------┬-------------+
                                                                                      │
                                                                                      │  snapshots
                                                                                      ▼
                                                                             MongoDB (repository)
                                                                                      ▲
+----------------------------+          GET /api/scraping/results                      │
|  Observatory (app.py)      |  ◀──────────────────────────────────────────────────────┘
|  Streamlit UI              |
+----------------------------+
```

**Core API routes** (as implemented in `backscrap/app/controller/`):
- `GET  /api/scraping/sources` — list available scraping sources
- `POST /api/scraping/run?source=<name>` — start background scraping for a source
- `GET  /api/scraping/results[?source=<name>]` — fetch stored results
- `GET  /api/events/status-stream` — server‑sent events with live updates

---

## Quickstart

> These commands come straight from the repository structure and files.

### 1) Backend (FastAPI)

Install backend dependencies and run the API:

```bash
pip install -r backscrap/requirements.txt
python backscrap/run.py
```

Default bind (per `run.py`): `http://0.0.0.0:9000`  
Interactive docs: `http://localhost:9000/docs`

---

### 2) Scheduler

Start the task scheduler to kick off scraping every **2 minutes** per source:

```bash
python scheduler/scheduler.py
```

It will:
1) fetch the available sources from `/api/scraping/sources`, and  
2) POST to `/api/scraping/run?source=<name>` on schedule.  
Logs are written to `scheduler.log`.

---

### 3) Observatory (Streamlit)

Install visualization dependencies and launch the dashboard:

```bash
pip install -r observatory/requirements.txt
streamlit run observatory/app.py
```

The UI reads snapshots from the API results endpoint (as coded in `observatory/app.py`).

---

## What you’ll see in the dashboard

- **Top market‑cap leaders** — identify dominant assets quickly.  
- **24h performance heatmap** — spot winners/losers and cross‑source divergences.  
- **Volume vs. market cap (log‑log)** — visualize liquidity vs. size.  
- **Price distribution by source** — assess provider dispersion for key tickers (e.g., BTC/ETH/SOL).  
- **Volatility ranking** — find the most turbulent assets via 24h % change std‑dev.  
- **Time‑series (when multiple snapshots exist)** — track price evolution for top symbols.

All fields referenced in charts (e.g., `price`, `change24h`, `volume24h`, `marketCap`, `timestamp`, `name`, `symbol`, `source`) are consumed exactly as produced by the backend.

---

## Repository layout (key paths)

```
backscrap/               # FastAPI service (controllers, repository, utils, run.py)
scheduler/               # Simple cron‑like loop using HTTP to trigger jobs
observatory/             # Streamlit UI for exploratory analysis
docs/                    # Additional documentation generated from the codebase
```

> This README intentionally reflects **only** what is present in the repository. Configuration and commands are derived from the existing files without external assumptions.

---