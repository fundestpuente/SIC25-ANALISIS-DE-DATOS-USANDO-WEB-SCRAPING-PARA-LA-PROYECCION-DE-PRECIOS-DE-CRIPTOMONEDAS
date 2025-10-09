"""Environment configuration loader (logic preserved).

Reads required environment variables for MongoDB and a DEV flag.
Keeps simple stdout prints for observability without changing behavior.
"""

from __future__ import annotations

import os
from typing import Final


def _get_required(name: str) -> str:
    value = os.environ.get(name, "")
    if not value:
        # Preserve fail-fast behavior for missing configuration.
        raise ValueError(f"Required environment variable '{name}' is not set.")
    return value


# Required environment variables
MONGO_DATABASE_URL: Final[str] = _get_required("MONGO_DATABASE_URL")
MONGO_DATABASE_NAME: Final[str] = _get_required("MONGO_DATABASE_NAME")

# Optional (defaults to False if missing)
DEV_MODE: Final[bool] = os.environ.get("DEV_MODE", "false").strip().lower() in ("true", "1", "yes")

# Keep the simple prints (same observable side-effects as typical original code)
print(f"MONGO_DATABASE_URL: {MONGO_DATABASE_URL}")
print(f"MONGO_DATABASE_NAME: {MONGO_DATABASE_NAME}")
