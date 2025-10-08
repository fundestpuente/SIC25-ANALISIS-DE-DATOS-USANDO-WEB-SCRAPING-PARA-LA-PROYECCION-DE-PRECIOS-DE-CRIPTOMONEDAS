from motor.motor_asyncio import AsyncIOMotorClient
from typing import Any, List
from bson import ObjectId
from typing import Union
from backscrap.app.pojo.enums.enumslist import ListaOperadoresCondicionales
from backscrap.app.utils.Global import Console

class MongoManager:
    """Clase base genérica para manejar conexiones a MongoDB."""
    _instance = None

    def __init__(self, mongo_uri, db_name):
        """Inicializa la conexión a MongoDB."""
        if not mongo_uri or not db_name:
            raise ValueError("Se deben proporcionar la URI y el nombre de la base de datos.")
        self.mongo_uri = mongo_uri
        self.client = AsyncIOMotorClient(self.mongo_uri)
        self.db = self.client[db_name]

    async def close_connection(self):
        """Cierra explícitamente la conexión a MongoDB."""
        if self.client:
            self.client.close()
            print("Conexión a MongoDB cerrada.")

    async def guardar(self, collection_name: str, document_data: dict) -> Union[str, None]:
        """
        Guarda un documento en la colección especificada.

        Args:
            collection_name (str): Nombre de la colección.
            document_data (dict): Datos del documento a guardar.
                Se recomienda que sea un diccionario válido para MongoDB.

        Returns:
            str: ID del documento insertado como cadena.
            None: Si ocurre un error durante la operación.
        """
        if not isinstance(document_data, dict):
            print("Error: document_data debe ser un diccionario.")
            return None

        try:
            collection = self.db[collection_name]
            result = await collection.insert_one(document_data)

            # Retornar el ID del documento insertado como cadena
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error al guardar documento en {collection_name}: {e}")
            return None
    
    async def actualizar(self, collection_name, document_id, document_data):
        """Actualiza un documento en la colección especificada."""
        collection = self.db[collection_name]

        # Verificar si el documento existe
        try:
            document = await collection.find_one({"_id": ObjectId(document_id)})
        except Exception as e:
            Console.log(f"Error al buscar documento: {e}")
            return 0

        if not document:
            Console.log(f"Documento con _id {document_id} no encontrado.")
            return 0

        # Verificar si hay cambios reales
        if all(document.get(key) == value for key, value in document_data.items()):
            Console.log("No se realizaron cambios; los datos ya están actualizados.")
            return 0

        # Intentar actualizar el documento
        result = await collection.update_one({"_id": ObjectId(document_id)}, {"$set": document_data})
        return result.modified_count
    
    async def recuperar(self, collection_name: str, document_id: str) -> dict:
        """
        Recupera un documento de la colección especificada por su _id.
        
        Args:
            collection_name (str): Nombre de la colección.
            document_id (str): ID del documento (en formato de cadena).
        
        Returns:
            dict: Documento recuperado con el campo "id" como cadena, o None si no se encuentra.
        """
        try:
            collection = self.db[collection_name]
            # Convertir document_id a ObjectId
            object_id = ObjectId(document_id)
            document = await collection.find_one({"_id": object_id})

            if document:
                # Convertir _id a id
                document["id"] = str(document["_id"])
                del document["_id"]
            return document
        except Exception as e:
            print(f"Error al recuperar documento: {e}")
            return None
    
    async def list(self, collection_name: str) -> list:
        """
        Recupera todos los documentos de la colección especificada.
        
        Args:
            collection_name (str): Nombre de la colección.
        
        Returns:
            list: Lista de documentos con el campo "id" como cadena.
        """
        try:
            collection = self.db[collection_name]
            cursor = collection.find()
            documents = await cursor.to_list(length=None)

            # Convertir _id a id en cada documento
            for document in documents:
                document["id"] = str(document["_id"])
                del document["_id"]

            return documents
        except Exception as e:
            print(f"Error al listar documentos: {e}")
            return []
    
    async def listWithCondition(
        self,
        collection_name: str,
        campo: str,
        mongo_operator: ListaOperadoresCondicionales,
        valor: Any = None
    ) -> List[dict]:
        """Recupera documentos de la colección especificada según una condición."""
        query = {}

        if campo == "_id":
            if isinstance(valor, list):
                valor = [ObjectId(v) if isinstance(v, str) else v for v in valor]
            else:
                valor = ObjectId(valor)

        # Construcción de la consulta según el operador
        if mongo_operator == ListaOperadoresCondicionales.EXISTS:
            query = {campo: {mongo_operator.value: True if valor else False}}
        elif mongo_operator == ListaOperadoresCondicionales.NOT_EXISTS:
            query = {campo: {mongo_operator.value: False}}
        elif mongo_operator == ListaOperadoresCondicionales.LIKE:
            query = {campo: {"$regex": valor, "$options": "i"}}
        elif mongo_operator in [ListaOperadoresCondicionales.IN, ListaOperadoresCondicionales.NOT_IN]:
            if not isinstance(valor, list):
                raise ValueError(f"El operador {mongo_operator} requiere una lista como valor.")
            query = {campo: {mongo_operator.value: valor}}
        else:
            query = {campo: {mongo_operator.value: valor}}

        # Ejecutar consulta con Motor
        collection = self.db[collection_name]
        cursor = collection.find(query)
        documents = await cursor.to_list(length=None)

        # Convertir _id a string para facilidad
        for document in documents:
            document["id"] = str(document["_id"])
            del document["_id"]

        return documents

