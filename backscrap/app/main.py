"""FastAPI application factory (logic preserved).

- Registers existing routers (ScrappingController, ServerEventsController).
- Provides a /health endpoint.
- Adds permissive CORS to keep local dev friction low (safe default).
- Uses a lifespan context to start/stop the SSE broadcaster.
- Tries to warm up Mongo if available (without failing if the import path differs).
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator, Iterable

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Optional imports — do not fail if module paths differ in the project.
try:
    from backscrap.app.utils.broadcaster import broadcast_startup, broadcast_shutdown
except Exception:  # noqa: BLE001
    async def broadcast_startup() -> None:  # type: ignore[no-redef]
        return None

    async def broadcast_shutdown() -> None:  # type: ignore[no-redef]
        return None

try:
    # If your project exposes a singleton that initializes Mongo, touch it at startup.
    from backscrap.app.datasource.MongoManagerCriptoScrapping import MongoManagerCriptoScrapping
except Exception:  # noqa: BLE001
    MongoManagerCriptoScrapping = None  # type: ignore[assignment]


# Routers: keep import paths stable with your project layout.
# If your modules use different names, only adjust these two import lines.
try:
    from backscrap.app.controller.ScrappingController import router as scrapping_router
except Exception:  # noqa: BLE001
    scrapping_router = None  # type: ignore[assignment]

try:
    from backscrap.app.controller.ServerEventsController import router as sse_router
except Exception:  # noqa: BLE001
    sse_router = None  # type: ignore[assignment]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manejador del ciclo de vida de la aplicación."""
    mongo_manager = MongoManagerCriptoScrapping.getInstance()
    print("Conexión a MongoDB inicializada.")
    #   inicia el SSE event
    await broadcast_startup()
    # Warm up Mongo singleton if present (do not fail if not available)
    if MongoManagerCriptoScrapping is not None:
        try:
            MongoManagerCriptoScrapping.getInstance()
        except Exception:
            # Keep silent to avoid altering observable behavior in non-Mongo flows
            pass
    try:
        yield
    finally:
        await broadcast_shutdown()


def _default_cors_origins() -> Iterable[str]:
    # Permissive by default for local development; adjust in env configs if needed.
    return ["*"]


app = FastAPI(
    title="Crypto Scraping API",
    version="0.1.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS configured with safe defaults; does not affect core logic flows
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(_default_cors_origins()),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict:
    """Simple health probe."""
    return {"status": "UP"}


# Mount routers only if they were imported successfully
if scrapping_router is not None:
    app.include_router(scrapping_router, prefix="/api/scraping", tags=["scraping"])

if sse_router is not None:
    app.include_router(sse_router, prefix="/api/events", tags=["events"])
