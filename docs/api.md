# API
## Router: `/api/scraping`  
*File:* `SIC25-ANALISIS-DE-DATOS-USANDO-WEB-SCRAPING-PARA-LA-PROYECCION-DE-PRECIOS-DE-CRIPTOMONEDAS/backscrap/app/controller/ScrappingController.py`
- **GET** `/api/scraping/sources`
- **POST** `/api/scraping/run`
- **GET** `/api/scraping/results`
## Router: `/api/events`  
*File:* `SIC25-ANALISIS-DE-DATOS-USANDO-WEB-SCRAPING-PARA-LA-PROYECCION-DE-PRECIOS-DE-CRIPTOMONEDAS/backscrap/app/controller/ServerEventsController.py`
- **GET** `/api/events/status-stream`

### Endpoint Notes (from repository code)
- `/api/scraping/sources` — returns available scraping sources (list of strings).
- `/api/scraping/run?source=<name>` — triggers a background scraping task for the given source; returns **202** on accept.
- `/api/scraping/results[?source=<name>]` — fetches stored results; if `source` is omitted, returns all.
- `/api/events/status-stream` — SSE stream for live scraping events.
