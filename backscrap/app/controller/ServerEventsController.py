"""Server-Sent Events (SSE) controller (logic preserved, English only).

Endpoint:
- GET /api/events/status-stream  → streams real-time task status updates

Behavior is unchanged: subscribes to the 'scraping_events' channel from the shared
broadcaster and yields incoming messages as SSE data frames.
"""

from __future__ import annotations

from typing import AsyncIterator, Dict, Any

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from backscrap.app.utils.broadcaster import broadcaster

router = APIRouter(
    prefix="/api/events",
    tags=["events"],
)


@router.get("/status-stream")
async def stream_status() -> EventSourceResponse:
    """SSE endpoint that streams real-time status updates for scraping tasks."""
    async def event_generator() -> AsyncIterator[Dict[str, Any]]:
        async with broadcaster.subscribe(channel="scraping_events") as subscriber:
            async for event in subscriber:
                # Yield the message payload; EventSourceResponse formats it as SSE.
                yield {"data": event.message}

    return EventSourceResponse(event_generator())
