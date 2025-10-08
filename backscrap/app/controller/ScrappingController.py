from fastapi import APIRouter, HTTPException, Query, BackgroundTasks

from typing import Optional
from backscrap.app.services.ScrappingService import ScrappingService
from backscrap.app.repository.ScrappingRepository import ScrappingRepository
from backscrap.app.utils.Global import ResponseUtil, Console

# Instancia del Repositorio y el Servicio de Scraping
repository = ScrappingRepository()
scrapping_service = ScrappingService(repository)

# Obtener dinámicamente las fuentes disponibles para la validación y documentación
AVAILABLE_SOURCES = scrapping_service.get_available_sources()

router = APIRouter(
    prefix="/api/scraping",
    tags=["Scraping"]
)

@router.get("/sources", response_model=list[str])
async def get_available_sources():
    """Devuelve una lista de todas las fuentes de scraping disponibles."""
    Console.log("Recibida solicitud para obtener las fuentes de scraping.")
    sources = AVAILABLE_SOURCES
    return sources

@router.post("/run", status_code=202)
async def run_scraping_task(
    background_tasks: BackgroundTasks,
    source: str = Query(
        ...,
        description="La fuente de datos a scrapear. Las opciones se obtienen dinámicamente del servicio.",
        enum=AVAILABLE_SOURCES
    )
):
    """
    Inicia una tarea de web scraping para la fuente especificada en segundo plano.
    La API responderá inmediatamente mientras la tarea se ejecuta.
    """
    Console.log(f"Recibida solicitud para iniciar scraping de: {source}")

    try:
        # Añade la tarea de larga duración (scraping) para que se ejecute en segundo plano
        background_tasks.add_task(scrapping_service.run_scraping_and_save, source)
        
        # Responde inmediatamente al cliente
        return {"message": f"Tarea de scraping para '{source}' iniciada en segundo plano."}

    except Exception as e:
        Console.error(f"Error al despachar la tarea de scraping: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno al iniciar la tarea: {str(e)}")

@router.get("/results")
async def get_scrapping_results(
    source: Optional[str] = Query(
        None,
        description="Opcional. Filtra los resultados por una fuente específica. Las opciones se obtienen dinámicamente.",
        enum=AVAILABLE_SOURCES
    )
):
    """
    Obtiene los resultados de scraping guardados en la base de datos.
    Se pueden filtrar por fuente.
    """
    Console.log(f"Recibida solicitud para obtener resultados de: {source or 'todas las fuentes'}")
    try:
        response = await scrapping_service.get_results(source)
        if response.status != 2: # Si no es 'success'
            raise HTTPException(status_code=404, detail=response.message)
        return response.data
    except Exception as e:
        Console.error(f"Error en el controlador al obtener resultados: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno al obtener resultados: {str(e)}")
