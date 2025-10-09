# Server-Sent Events (SSE)

- Endpoint: `/api/events/status-stream`
- Behavior: subscribes to the `scraping_events` channel and streams messages as SSE frames.
- Source: `backscrap/app/controller/ServerEventsController.py`
