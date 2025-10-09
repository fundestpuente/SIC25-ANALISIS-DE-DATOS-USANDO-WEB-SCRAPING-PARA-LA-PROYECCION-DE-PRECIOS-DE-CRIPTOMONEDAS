"""SSE broadcaster bootstrap (logic preserved).

Keeps an in-memory broadcaster. For multi-worker deployments you can switch
to Redis by replacing the URL with something like: 'redis://localhost:6379/0'.
"""

from __future__ import annotations

from typing import Final

from broadcaster import Broadcast

# In-memory backend to preserve simple single-process behavior
broadcaster: Final[Broadcast] = Broadcast("memory://")


async def broadcast_startup() -> None:
    """Connect the broadcaster (to be called on app startup)."""
    await broadcaster.connect()


async def broadcast_shutdown() -> None:
    """Disconnect the broadcaster (to be called on app shutdown)."""
    await broadcaster.disconnect()
