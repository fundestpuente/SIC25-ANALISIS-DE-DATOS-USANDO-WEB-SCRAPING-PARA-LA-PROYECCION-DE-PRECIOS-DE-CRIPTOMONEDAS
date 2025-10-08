import requests
import schedule
import sys
import time
import logging

# Configuración básica de logging para el scheduler
logging.basicConfig(
    filename="scheduler.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# La URL base de tu API. Asegúrate de que el puerto coincida con el de run.py
API_BASE_URL = "http://localhost:9000"

def get_dynamic_sources() -> list[str]:
    """Obtiene la lista de fuentes de scraping disponibles directamente desde la API."""
    sources_endpoint = f"{API_BASE_URL}/api/scraping/sources"
    try:
        response = requests.get(sources_endpoint, timeout=5)
        response.raise_for_status()  # Lanza excepción para errores 4xx/5xx
        sources = response.json()
        if isinstance(sources, list) and sources:
            logging.info(f"Fuentes obtenidas dinámicamente de la API: {sources}")
            return sources
        else:
            logging.warning("La API no devolvió ninguna fuente para planificar.")
            return []
    except requests.RequestException as e:
        # Error crítico si no podemos contactar la API para obtener la configuración inicial
        logging.critical(f"No se pudo conectar a la API para obtener las fuentes en {sources_endpoint}. Error: {e}")
        return []

def trigger_scraping_job(source: str):
    """Función que llama al endpoint de la API para iniciar un scraping."""
    endpoint = f"{API_BASE_URL}/api/scraping/run?source={source}"
    try:
        response = requests.post(endpoint, timeout=10)
        if response.status_code == 202:
            logging.info(f"Tarea de scraping para '{source}' iniciada correctamente.")
            print(f"Tarea para '{source}' iniciada.")
        else:
            logging.error(f"Error al iniciar la tarea para '{source}'. Status: {response.status_code}, Body: {response.text}")
            print(f"Error al iniciar tarea para '{source}'. Revisa scheduler.log")
    except requests.RequestException as e:
        logging.error(f"No se pudo conectar a la API en {endpoint}. Error: {e}")
        print(f"No se pudo conectar a la API para iniciar la tarea de '{source}'. ¿Está el servidor FastAPI corriendo?")

if __name__ == "__main__":
    print("🚀 Iniciando planificador de tareas de scraping...")
    
    # Obtenemos las fuentes de forma dinámica
    sources_to_scrape = get_dynamic_sources()

    if not sources_to_scrape:
        print("❌ No se pudieron obtener las fuentes desde la API o la lista está vacía. El planificador no se iniciará.")
        sys.exit(1) # Salimos del script si no hay nada que hacer

    print(f"✅ Planificador listo. Se ejecutarán tareas para: {', '.join(sources_to_scrape)}.")
    print("Cada tarea se ejecutará cada 2 minutos.")

    # Planificar la ejecución para cada fuente
    for src in sources_to_scrape:
        schedule.every(2).minutes.do(trigger_scraping_job, source=src)

    # Bucle infinito para que el planificador siga corriendo
    while True:
        schedule.run_pending()
        time.sleep(1)