# Troubleshooting

- **Cannot reach API**: Ensure `python backscrap/run.py` is running and the port matches the observatory `API_URL` constant.
- **No data shown in Streamlit**: The API must return snapshots; run the scheduler or trigger `/api/scraping/run?source=<name>` manually.
- **CORS errors** (browser clients): This stack is typically consumed by Streamlit (server-side). If you add a browser client, configure CORS in the FastAPI app accordingly (refer to `backscrap/app/main.py`).
