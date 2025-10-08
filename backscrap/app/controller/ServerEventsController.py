from fastapi import APIRouter, HTTPException, Query, BackgroundTasks

from backscrap.app.utils.broadcaster import broadcaster
from sse_starlette.sse import EventSourceResponse

router = APIRouter(
    prefix="/api/events",
    tags=["events"]
)

@router.get("/status-stream")
async def stream_status():
    """
    Endpoint SSE que envía actualizaciones en tiempo real sobre el estado de las tareas.
    """
    async def event_generator():
        async with broadcaster.subscribe(channel="scraping_events") as subscriber:
            async for event in subscriber:
                yield {"data": event.message}
    return EventSourceResponse(event_generator())
