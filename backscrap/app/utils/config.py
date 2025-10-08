
from dotenv import load_dotenv
import os

# Cargar las variables de entorno
load_dotenv()

MONGO_DATABASE_URL = os.getenv("MONGO_DATABASE_URL") # Obtener URI de conexión
if not MONGO_DATABASE_URL:
    raise ValueError("La variable de entorno 'MONGO_DATABASE_URL' no está configurada.")

MONGO_DATABASE_NAME = os.getenv("MONGO_DATABASE_NAME")
if not MONGO_DATABASE_NAME:
    raise ValueError("La variable de entorno 'MONGO_DATABASE_NAME' no está configurada.")

DEV_MODE = os.getenv("DEV_MODE", "false").strip().lower() in ("true", "1", "yes")

print(f"MONGO_DATABASE_URL: {MONGO_DATABASE_URL}")
print(f"MONGO_DATABASE_NAME: {MONGO_DATABASE_NAME}")