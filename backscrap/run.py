"""Uvicorn entrypoint (logic preserved).

Starts the FastAPI app on host 0.0.0.0 and port 9000.
Maintains error logging to a file and same observable behavior.
"""

from __future__ import annotations

import logging

import uvicorn
from app.main import app  # Path kept identical to common project layouts

# File logging (same semantics as typical original script)
logging.basicConfig(
    filename="run.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


if __name__ == "__main__":
    try:
        uvicorn.run(app, host="0.0.0.0", port=9000)
    except Exception as exc:  # noqa: BLE001
        logging.error("Application startup error: %s", exc)
        print(f"An error occurred: {exc}")
