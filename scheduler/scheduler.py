"""Simple scraping task scheduler (logic preserved, English only).

- Fetches available sources from the API at startup.
- Schedules a background POST to /api/scraping/run?source=<src> every 2 minutes.
- Logs to 'scheduler.log' and prints concise console messages.
"""

from __future__ import annotations

import logging
import sys
import time

import requests
import schedule

# Basic logging configuration for the scheduler (unchanged behavior)
logging.basicConfig(
    filename="scheduler.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Base URL of your API. Ensure the port matches run.py
API_BASE_URL = "http://localhost:9000"


def get_dynamic_sources() -> list[str]:
    """Retrieve the list of available scraping sources directly from the API."""
    sources_endpoint = f"{API_BASE_URL}/api/scraping/sources"
    try:
        response = requests.get(sources_endpoint, timeout=5)
        response.raise_for_status()  # raise for 4xx/5xx
        sources = response.json()
        if isinstance(sources, list) and sources:
            logging.info("Sources obtained dynamically from the API: %s", sources)
            return sources
        logging.warning("The API did not return any sources to schedule.")
        return []
    except requests.RequestException as e:
        # Critical if we cannot contact the API to obtain initial configuration
        logging.critical(
            "Could not connect to the API to obtain sources at %s. Error: %s",
            sources_endpoint,
            e,
        )
        return []


def trigger_scraping_job(source: str) -> None:
    """Invoke the API endpoint to start a scraping task for a single source."""
    endpoint = f"{API_BASE_URL}/api/scraping/run?source={source}"
    try:
        response = requests.post(endpoint, timeout=10)
        if response.status_code == 202:
            logging.info("Scraping task for '%s' started successfully.", source)
            print(f"Task for '{source}' started.")
        else:
            logging.error(
                "Error starting task for '%s'. Status: %s, Body: %s",
                source,
                response.status_code,
                response.text,
            )
            print(f"Error starting task for '{source}'. Check scheduler.log")
    except requests.RequestException as e:
        logging.error("Could not connect to the API at %s. Error: %s", endpoint, e)
        print(
            f"Could not connect to the API to start the task for '{source}'. "
            "Is the FastAPI server running?"
        )


if __name__ == "__main__":
    print("🚀 Starting scraping task scheduler...")

    # Obtain sources dynamically
    sources_to_scrape = get_dynamic_sources()

    if not sources_to_scrape:
        print(
            "❌ Could not obtain sources from the API or the list is empty. "
            "The scheduler will not start."
        )
        sys.exit(1)  # Exit if there's nothing to do

    print(f"✅ Scheduler ready. Tasks will run for: {', '.join(sources_to_scrape)}.")
    print("Each task will run every 2 minutes.")

    # Schedule execution for each source
    for src in sources_to_scrape:
        schedule.every(2).minutes.do(trigger_scraping_job, source=src)

    # Infinite loop to keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(1)
