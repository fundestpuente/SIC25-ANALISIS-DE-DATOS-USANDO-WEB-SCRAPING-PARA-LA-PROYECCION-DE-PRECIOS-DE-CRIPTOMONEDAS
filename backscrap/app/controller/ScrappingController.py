"""Scraping API controller (logic preserved, English-only messaging).

Endpoints:
- GET  /api/scraping/sources      → list available scraping sources
- POST /api/scraping/run          → start a background scraping task for a given source
- GET  /api/scraping/results      → fetch stored scraping results (optionally filtered by source)

All runtime behavior and control flow remain unchanged.
"""

from __future__ import annotations

from typing import Optional, Any, List

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks

from backscrap.app.services.ScrappingService import ScrappingService
from backscrap.app.repository.ScrappingRepository import ScrappingRepository
from backscrap.app.utils.Global import ResponseUtil, Console  # ResponseUtil kept for compatibility

# Instantiate repository and service (same behavior as before)
repository = ScrappingRepository()
scrapping_service = ScrappingService(repository)

# Dynamically obtain available sources for validation and documentation (evaluated at import time)
AVAILABLE_SOURCES: List[str] = scrapping_service.get_available_sources()

router = APIRouter(
    prefix="/api/scraping",
    tags=["Scraping"],
)


@router.get("/sources", response_model=list[str])
async def get_available_sources() -> list[str]:
    """Return a list of all available scraping sources."""
    Console.log("Received request: list available scraping sources.")
    sources = AVAILABLE_SOURCES
    return sources


@router.post("/run", status_code=202)
async def run_scraping_task(
    background_tasks: BackgroundTasks,
    source: str = Query(
        ...,
        description="The data source to scrape. Options are obtained dynamically from the service.",
        enum=AVAILABLE_SOURCES,
    ),
) -> dict:
    """Start a background web-scraping task for the specified source.

    The API responds immediately while the task runs in the background.
    """
    Console.log(f"Received request: start scraping for source '{source}'.")

    try:
        # Schedule the long-running scraping task in background (logic preserved)
        background_tasks.add_task(scrapping_service.run_scraping_and_save, source)

        # Immediate response to the client
        return {"message": f"Scraping task for '{source}' started in the background."}

    except Exception as e:  # noqa: BLE001
        Console.error(f"Error dispatching scraping task: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error when starting the task: {str(e)}")


@router.get("/results")
async def get_scrapping_results(
    source: Optional[str] = Query(
        None,
        description="Optional. Filter results by a specific source. Options are obtained dynamically.",
        enum=AVAILABLE_SOURCES,
    ),
) -> Any:
    """Fetch stored scraping results, optionally filtered by source."""
    Console.log(f"Received request: fetch results for source '{source or 'all sources'}'.")
    try:
        response = await scrapping_service.get_results(source)
        # If not success (status != 2), return 404 with the service message (logic preserved)
        if response.status != 2:
            raise HTTPException(status_code=404, detail=response.message)
        return response.data
    except Exception as e:  # noqa: BLE001
        Console.error(f"Controller error while fetching results: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error when fetching results: {str(e)}")
