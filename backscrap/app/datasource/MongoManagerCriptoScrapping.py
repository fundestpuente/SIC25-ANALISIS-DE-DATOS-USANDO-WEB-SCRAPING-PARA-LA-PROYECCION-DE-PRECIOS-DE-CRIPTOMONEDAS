from motor.motor_asyncio import AsyncIOMotorClient
from backscrap.app.datasource.MongoManager import MongoManager
from backscrap.app.utils.config import MONGO_DATABASE_URL, MONGO_DATABASE_NAME

class MongoManagerCriptoScrapping(MongoManager):
    _instance = None

    @staticmethod
    def getInstance():
        """Obtiene la instancia única de la clase."""
        if MongoManagerCriptoScrapping._instance is None:
            MongoManagerCriptoScrapping._instance = MongoManagerCriptoScrapping()
        return MongoManagerCriptoScrapping._instance

    def __init__(self):
        """Inicializa la conexión para la base de datos `CriptoScrapping`."""
        if MongoManagerCriptoScrapping._instance is not None:
            raise Exception("Esta clase es un singleton. Usa getInstance() para obtener la instancia.")
        
        # Inicializar los valores antes de llamar a la clase base
        # Configurar valores específicos para la base de datos `CriptoScrapping`
        self.mongo_uri = MONGO_DATABASE_URL
         # Nombre específico de la base de datos
        self.db_name = MONGO_DATABASE_NAME

        # Llamar al constructor de la clase base con los argumentos necesarios
        super().__init__(self.mongo_uri, self.db_name)