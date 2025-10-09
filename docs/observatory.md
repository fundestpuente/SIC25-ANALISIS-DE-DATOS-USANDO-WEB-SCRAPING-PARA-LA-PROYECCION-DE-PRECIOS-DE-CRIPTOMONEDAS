# Observatory (Streamlit)

- Install dependencies: `pip install -r observatory/requirements.txt`
- Run: `streamlit run observatory/app.py`

## Charts & Expected Fields
The dashboard uses the following fields in the API results:
- `price`
- `change24h`
- `volume24h`
- `marketCap`
- `timestamp`
- `name`
- `symbol`
- `source`

These fields are referenced directly in `observatory/app.py` found in this repository.
