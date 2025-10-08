from broadcaster import Broadcast

# Usamos un backend en memoria para simplicidad.
# Para producción con múltiples workers, se cambiaría a:
# broadcaster = Broadcast("redis://localhost:6379")
broadcaster = Broadcast("memory://")

async def broadcast_startup():
    await broadcaster.connect()

async def broadcast_shutdown():
    await broadcaster.disconnect()