from datetime import datetime
from backscrap.app.datasource.MongoManagerCriptoScrapping import MongoManagerCriptoScrapping
from backscrap.app.pojo.enums.enumslist import ListaCollecciones, ListaOperadoresCondicionales
from backscrap.app.utils.Global import ResponseUtil, Console

class ScrappingRepository:
    def __init__(self):
        self.database = MongoManagerCriptoScrapping.getInstance()

    async def save_scrapping_results(self, source: str, timestamp: datetime, records: list):
        """
        Guarda un lote de resultados de scraping en la base de datos.
        """
        document_to_save = {
            "source": source,
            "timestamp": timestamp,
            "data": records
        }

        try:
            inserted_id = await self.database.guardar(
                ListaCollecciones.ScrappingResults.value, 
                document_to_save
            )
            if inserted_id:
                return ResponseUtil.success("Resultados del scraping guardados con éxito.", data={"id": inserted_id})
            else:
                return ResponseUtil.error("No se pudo guardar el documento en la base de datos.")
        except Exception as e:
            Console.error(f"Error en ScrappingRepository al guardar: {e}")
            return ResponseUtil.error(f"Error al guardar los resultados del scraping: {str(e)}")

    async def get_scrapping_results(self, source: str = None):
        """
        Recupera los resultados de scraping de la base de datos.
        Puede filtrar por fuente si se proporciona.
        """
        try:
            if source:
                # Usa listWithCondition para filtrar por fuente
                results = await self.database.listWithCondition(
                    ListaCollecciones.ScrappingResults.value,
                    "source",
                    ListaOperadoresCondicionales.EQUAL,
                    source
                )
            else:
                # Obtiene todos los documentos si no se especifica una fuente
                results = await self.database.list(ListaCollecciones.ScrappingResults.value)
            return ResponseUtil.success("Resultados recuperados con éxito.", data=results)
        except Exception as e:
            Console.error(f"Error en ScrappingRepository al obtener resultados: {e}")
            return ResponseUtil.error(f"Error al obtener los resultados del scraping: {str(e)}")