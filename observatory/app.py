import pandas as pd
import streamlit as st
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import requests

# Constante para la URL de la API
API_URL = "http://localhost:9000/api/scraping/results"
# ========== CONFIGURACIÓN DE LA PÁGINA ==========
st.set_page_config(
    page_title="Crypto Market Observatory",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Crypto Market Observatory")
st.caption("Datos integrados de CoinGecko y CoinMarketCap")


@st.cache_data(ttl=60) # Cachea los datos por 60 segundos
def load_data():
    """Carga los datos desde la API, los procesa y devuelve un DataFrame."""
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        raw_data = response.json()

        records = []
        for entry in raw_data:
            for d in entry["data"]:
                d["source"] = entry["source"]
                d["timestamp"] = pd.to_datetime(entry["timestamp"])
                records.append(d)
        
        if not records:
            return pd.DataFrame()

        return pd.DataFrame(records)
    except requests.RequestException as e:
        st.error(f"Error al conectar con la API: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Ocurrió un error inesperado al procesar los datos: {e}")
        return pd.DataFrame()

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia y convierte los tipos de datos de las columnas numéricas."""
    if df.empty:
        return df
        
    for col in ["price", "change24h", "volume24h", "marketCap"]:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(r"[+$,%]", "", regex=True)
            .pipe(pd.to_numeric, errors='coerce')
        )
    return df

def display_sidebar(df: pd.DataFrame):
    """Muestra la barra lateral con filtros y devuelve las fuentes seleccionadas."""
    st.sidebar.header("⚙️ Filtros de visualización")
    
    if st.sidebar.button("Forzar actualización de datos"):
        st.cache_data.clear()
        st.rerun()

    if df.empty:
        st.sidebar.warning("No hay datos para filtrar.")
        return []

    all_sources = df["source"].unique()
    selected_sources = st.sidebar.multiselect(
        "Selecciona fuente de datos",
        options=all_sources,
        default=all_sources
    )
    return selected_sources


df_raw = load_data()

if df_raw.empty:
    st.warning("No se pudieron cargar los datos. Por favor, verifica que el backend esté funcionando y que haya datos en la base de datos.")
else:
    df_cleaned = clean_data(df_raw.copy())
    selected_sources = display_sidebar(df_cleaned)
    df_filtered = df_cleaned[df_cleaned["source"].isin(selected_sources)]

    if df_filtered.empty:
        st.info("Selecciona al menos una fuente de datos en la barra lateral para ver los gráficos.")
    else:
        # ========== 1️⃣ TOP 10 POR CAPITALIZACIÓN ==========
        with st.container(border=True):
            st.subheader("💰 Top 10 Criptomonedas por Capitalización de Mercado")
            top_market_cap = df_filtered.groupby("name", as_index=False)["marketCap"].mean().nlargest(10, "marketCap")
            fig1 = px.bar(
                top_market_cap, x="marketCap", y="name", orientation="h", color="marketCap",
                color_continuous_scale="Blues", title="Capitalización de Mercado Promedio (Top 10)"
            )
            st.plotly_chart(fig1, use_container_width=True)
            with st.expander("ℹ️ ¿Qué significa este gráfico?"):
                st.markdown("""
                Este gráfico de barras muestra las 10 criptomonedas con la mayor **capitalización de mercado promedio**. La capitalización de mercado (Market Cap) se calcula multiplicando el precio actual de una moneda por su oferta circulante.
                - **Uso**: Permite identificar rápidamente las criptomonedas más grandes y establecidas del mercado.
                - **Interpretación**: Una mayor capitalización de mercado generalmente indica una mayor adopción y estabilidad.
                """)

        # ========== 2️⃣ HEATMAP DE VARIACIÓN 24H ==========
        with st.container(border=True):
            st.subheader("🌡️ Heatmap de Variación Porcentual (24h)")
            pivot = df_filtered.pivot_table(values="change24h", index="name", columns="source", aggfunc="mean")
            fig2, ax = plt.subplots(figsize=(8, 8))
            sns.heatmap(pivot.dropna(), cmap="RdYlGn", center=0, annot=True, fmt=".2f", ax=ax)
            st.pyplot(fig2)
            with st.expander("ℹ️ ¿Qué significa este gráfico?"):
                st.markdown("""
                Este mapa de calor compara el **cambio porcentual promedio en las últimas 24 horas** para cada criptomoneda, según las diferentes fuentes de datos.
                - **Colores**: El verde indica una ganancia de precio, el rojo una pérdida y el amarillo/blanco un cambio cercano a cero.
                - **Uso**: Es útil para visualizar el rendimiento reciente del mercado y detectar discrepancias de precios entre las fuentes.
                """)

        # ========== 3️⃣ SCATTER: VOLUMEN VS CAPITALIZACIÓN ==========
        with st.container(border=True):
            st.subheader("⚖️ Relación entre Volumen y Capitalización")
            fig3 = px.scatter(
                df_filtered.dropna(subset=['marketCap', 'volume24h', 'price']),
                x="marketCap", y="volume24h", color="name", size="price", hover_name="name",
                facet_col="source", log_x=True, log_y=True, title="Volumen (24h) vs. Capitalización de Mercado"
            )
            st.plotly_chart(fig3, use_container_width=True)
            with st.expander("ℹ️ ¿Qué significa este gráfico?"):
                st.markdown("""
                Este gráfico de dispersión explora la relación entre la **capitalización de mercado** (eje X) y el **volumen de transacciones en 24 horas** (eje Y). Ambos ejes están en escala logarítmica para visualizar mejor los datos.
                - **Tamaño de la burbuja**: Representa el precio de la criptomoneda.
                - **Uso**: Ayuda a entender si las monedas con alta capitalización también tienen un alto volumen de negociación, lo que puede ser un indicador de liquidez y actividad del mercado.
                """)

        # ========== 4️⃣ COMPARATIVA DE PRECIOS ENTRE FUENTES ==========
        with st.container(border=True):
            st.subheader("📈 Comparativa de Precios por Fuente")
            top_coins = df_filtered[df_filtered["symbol"].isin(["BTC", "ETH", "SOL", "BNB", "USDT"])]
            fig4 = px.box(
                top_coins, x="symbol", y="price", color="source",
                title="Distribución de Precios para Criptos Principales"
            )
            st.plotly_chart(fig4, use_container_width=True)
            with st.expander("ℹ️ ¿Qué significa este gráfico?"):
                st.markdown("""
                Este diagrama de cajas (box plot) muestra la **distribución de los precios** registrados para las principales criptomonedas a través de las diferentes fuentes y a lo largo del tiempo.
                - **Interpretación**: Las "cajas" más altas indican una mayor variabilidad o dispersión en los precios reportados. Permite comparar si una fuente tiende a reportar precios consistentemente más altos o más bajos que otra.
                """)

        # ========== 5️⃣ PARTICIPACIÓN DE MERCADO (DONUT) ==========
        with st.container(border=True):
            st.subheader("🪙 Participación de Mercado (Top 8)")
            market_share = df_filtered.groupby("name", as_index=False)["marketCap"].mean().nlargest(8, "marketCap")
            fig5 = px.pie(
                market_share, values="marketCap", names="name", title="Distribución del Valor de Mercado (Top 8)",
                hole=0.5, color_discrete_sequence=px.colors.sequential.Tealgrn
            )
            st.plotly_chart(fig5, use_container_width=True)
            with st.expander("ℹ️ ¿Qué significa este gráfico?"):
                st.markdown("""
                Este gráfico de dona ilustra la **cuota de mercado** de las 8 criptomonedas con mayor capitalización.
                - **Uso**: Muestra qué proporción del valor total del mercado (de este top 8) corresponde a cada moneda, destacando el dominio de las principales criptomonedas como Bitcoin y Ethereum.
                """)

        # ========== 6️⃣ VOLATILIDAD (STD DE CAMBIO 24H) ==========
        with st.container(border=True):
            st.subheader("⚔️ Ranking de Volatilidad")
            volatility = df_filtered.groupby("symbol")["change24h"].std().sort_values(ascending=False).head(10)
            fig6 = px.bar(
                x=volatility.values, y=volatility.index, orientation="h", color=volatility.values,
                color_continuous_scale="Reds", title="Top 10 Criptomonedas más Volátiles"
            )
            st.plotly_chart(fig6, use_container_width=True)
            with st.expander("ℹ️ ¿Qué significa este gráfico?"):
                st.markdown("""
                Este gráfico clasifica las 10 criptomonedas más **volátiles** basándose en la desviación estándar de su cambio de precio en 24 horas.
                - **Interpretación**: Una barra más larga significa que el precio de esa moneda ha fluctuado más drásticamente. La volatilidad puede representar tanto una oportunidad de ganancia como un mayor riesgo.
                """)

        # ========== 7️⃣ LÍNEA TEMPORAL (SI EXISTEN VARIOS SNAPSHOTS) ==========
        if df_filtered["timestamp"].nunique() > 1:
            with st.container(border=True):
                st.subheader("📅 Evolución Temporal de Precios")
                line_data = df_filtered[df_filtered["symbol"].isin(["BTC", "ETH", "SOL"])]
                fig7 = px.line(
                    line_data, x="timestamp", y="price", color="symbol",
                    title="Evolución del Precio (BTC, ETH, SOL)"
                )
                st.plotly_chart(fig7, use_container_width=True)
                with st.expander("ℹ️ ¿Qué significa este gráfico?"):
                    st.markdown("""
                    Este gráfico de líneas muestra la **evolución del precio** a lo largo del tiempo para algunas de las criptomonedas más importantes.
                    - **Uso**: Es ideal para observar tendencias, patrones y la volatilidad de los precios a lo largo de las diferentes capturas de datos.
                    """)

st.markdown(
    """
    <style>
    body {
        background-color: #0e1117;
        color: #f5f6fa;
    }
    .stPlotlyChart {
        border-radius: 8px;
    }
    div[data-testid="stContainer"] {
        border-radius: 10px !important;
        background-color: #1c1e25;
    }
    div[data-testid="stExpander"] {
        background-color: #262730;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("---")
st.caption("© 2025 | Streamlit - Plotly - Python")
