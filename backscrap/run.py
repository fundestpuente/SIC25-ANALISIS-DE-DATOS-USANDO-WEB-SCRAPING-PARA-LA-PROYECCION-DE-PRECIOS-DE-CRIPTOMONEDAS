import uvicorn
import logging
from app.main import app

# Configurar logging
logging.basicConfig(
    filename="run.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

if __name__ == "__main__":
    try:
        uvicorn.run(app, host="0.0.0.0", port=9000)
    except Exception as e:
        logging.error(f"Error al iniciar la aplicación: {e}")
        print(f"Ocurrió un error: {e}")