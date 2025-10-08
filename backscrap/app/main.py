from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backscrap.app.controller.ScrappingController import router as api_scrapping_router
from backscrap.app.controller.ServerEventsController import router as api_sse
from backscrap.app.datasource.MongoManagerCriptoScrapping import MongoManagerCriptoScrapping
from backscrap.app.utils.broadcaster import broadcast_startup, broadcast_shutdown

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manejador del ciclo de vida de la aplicación."""
    # Inicio: Inicializa los recursos (por ejemplo, conexión a MongoDB)
    mongo_manager = MongoManagerCriptoScrapping.getInstance()
    print("Conexión a MongoDB inicializada.")
    #   inicia el SSE event
    await broadcast_startup()

    yield  # Aquí la aplicación estará ejecutándose

    # Apagado: Libera los recursos
    await mongo_manager.close_connection()
    await broadcast_shutdown()
    print("Conexión a MongoDB cerrada.")

# Se pasa el lifespan al crear la instancia de FastAPI
app = FastAPI(lifespan=lifespan)

# Configura el middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def root():
    return {"status": "UP"}

# Incluir el enrutador de items en la aplicación principal
app.include_router(api_scrapping_router)
app.include_router(api_sse)