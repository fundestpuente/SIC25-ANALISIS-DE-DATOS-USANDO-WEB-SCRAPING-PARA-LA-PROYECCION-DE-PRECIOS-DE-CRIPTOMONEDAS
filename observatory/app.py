"""Streamlit dashboard for visualizing scraped crypto data (logic preserved).

- Reads snapshots from the FastAPI endpoint.
- Normalizes records and renders several charts with Plotly and Seaborn.
- Keeps the same column expectations: price, change24h, volume24h, marketCap.
- UI text/messages are now in English only. Behavior is unchanged.
"""

from __future__ import annotations

from typing import List

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import requests
import seaborn as sns
import streamlit as st

# ===== API URL (unchanged logic) =====
API_URL = "http://localhost:9000/api/scraping/results"

# ===== PAGE CONFIG =====
st.set_page_config(
    page_title="Crypto Market Observatory",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📊 Crypto Market Observatory")
st.caption("Integrated data from CoinGecko and CoinMarketCap")

# ===== DATA FUNCTIONS =====


@st.cache_data(ttl=60)  # cache data for 60 seconds
def load_data() -> pd.DataFrame:
    """Fetch data from the API, normalize records, and return a DataFrame."""
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
        st.error(f"Error connecting to the API: {e}")
        return pd.DataFrame()
    except Exception as e:  # noqa: BLE001
        st.error(f"An unexpected error occurred while processing the data: {e}")
        return pd.DataFrame()


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and cast numeric columns to proper dtypes (logic preserved)."""
    if df.empty:
        return df

    for col in ["price", "change24h", "volume24h", "marketCap"]:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(r"[+$,%]", "", regex=True)
            .pipe(pd.to_numeric, errors="coerce")
        )
    return df


def display_sidebar(df: pd.DataFrame) -> List[str]:
    """Render sidebar filters and return the selected sources (logic preserved)."""
    st.sidebar.header("⚙️ Display filters")

    if st.sidebar.button("Force data refresh"):
        st.cache_data.clear()
        st.rerun()

    if df.empty:
        st.sidebar.warning("No data available to filter.")
        return []

    all_sources = df["source"].unique()
    selected_sources = st.sidebar.multiselect(
        "Select data source(s)",
        options=all_sources,
        default=all_sources,
    )
    return selected_sources


df_raw = load_data()

if df_raw.empty:
    st.warning(
        "Data could not be loaded. Please verify the backend is running and the database has snapshots."
    )
else:
    df_cleaned = clean_data(df_raw.copy())
    selected_sources = display_sidebar(df_cleaned)
    df_filtered = df_cleaned[df_cleaned["source"].isin(selected_sources)]

    if df_filtered.empty:
        st.info("Select at least one data source in the sidebar to view the charts.")
    else:
        # ===== 1️⃣ TOP 10 BY MARKET CAP =====
        with st.container(border=True):
            st.subheader("💰 Top 10 Cryptocurrencies by Market Capitalization")
            top_market_cap = (
                df_filtered.groupby("name", as_index=False)["marketCap"]
                .mean()
                .nlargest(10, "marketCap")
            )
            fig1 = px.bar(
                top_market_cap,
                x="marketCap",
                y="name",
                orientation="h",
                color="marketCap",
                color_continuous_scale="Blues",
                title="Average Market Capitalization (Top 10)",
            )
            st.plotly_chart(fig1, use_container_width=True)
            with st.expander("ℹ️ What does this chart show?"):
                st.markdown(
                    """
                    This horizontal bar chart shows the **Top 10 cryptocurrencies by average market capitalization**.
                    - **Use case**: Quickly identify the largest, most established assets.
                    - **Interpretation**: Higher market cap usually indicates broader adoption and relative stability.
                    """
                )

        # ===== 2️⃣ 24H CHANGE HEATMAP =====
        with st.container(border=True):
            st.subheader("🌡️ 24h Percentage Change Heatmap")
            pivot = df_filtered.pivot_table(
                values="change24h", index="name", columns="source", aggfunc="mean"
            )
            fig2, ax = plt.subplots(figsize=(8, 8))
            sns.heatmap(pivot.dropna(), cmap="RdYlGn", center=0, annot=True, fmt=".2f", ax=ax)
            st.pyplot(fig2)
            with st.expander("ℹ️ What does this chart show?"):
                st.markdown(
                    """
                    This heatmap compares the **average 24-hour percent change** per cryptocurrency across data sources.
                    - **Colors**: Green = gain, Red = loss, Yellow/white ≈ near zero change.
                    - **Use case**: Spot recent performance and cross-source discrepancies at a glance.
                    """
                )

        # ===== 3️⃣ VOLUME VS MARKET CAP (SCATTER) =====
        with st.container(border=True):
            st.subheader("⚖️ Volume vs. Market Capitalization")
            fig3 = px.scatter(
                df_filtered.dropna(subset=["marketCap", "volume24h", "price"]),
                x="marketCap",
                y="volume24h",
                color="name",
                size="price",
                hover_name="name",
                facet_col="source",
                log_x=True,
                log_y=True,
                title="24h Volume vs. Market Capitalization",
            )
            st.plotly_chart(fig3, use_container_width=True)
            with st.expander("ℹ️ What does this chart show?"):
                st.markdown(
                    """
                    This scatter plot explores the relationship between **market capitalization** (x-axis) and
                    **24h trading volume** (y-axis). Both axes are in log scale to better spread the data.
                    - **Bubble size**: current price
                    - **Use case**: Understand if large-cap assets also have high trading volume (liquidity/activity).
                    """
                )

        # ===== 4️⃣ PRICE COMPARISON ACROSS SOURCES =====
        with st.container(border=True):
            st.subheader("📈 Price Comparison by Source")
            top_coins = df_filtered[df_filtered["symbol"].isin(["BTC", "ETH", "SOL", "BNB", "USDT"])]
            fig4 = px.box(
                top_coins,
                x="symbol",
                y="price",
                color="source",
                title="Price Distribution for Major Cryptos",
            )
            st.plotly_chart(fig4, use_container_width=True)
            with st.expander("ℹ️ What does this chart show?"):
                st.markdown(
                    """
                    This box plot displays the **price distribution** for top cryptocurrencies across sources and over time.
                    - **Interpretation**: Taller boxes indicate higher variability. Check if a source consistently reports
                      higher/lower prices than others.
                    """
                )

        # ===== 5️⃣ MARKET SHARE (DONUT) =====
        with st.container(border=True):
            st.subheader("🪙 Market Share (Top 8)")
            market_share = (
                df_filtered.groupby("name", as_index=False)["marketCap"]
                .mean()
                .nlargest(8, "marketCap")
            )
            fig5 = px.pie(
                market_share,
                values="marketCap",
                names="name",
                title="Market Value Distribution (Top 8)",
                hole=0.5,
                color_discrete_sequence=px.colors.sequential.Tealgrn,
            )
            st.plotly_chart(fig5, use_container_width=True)
            with st.expander("ℹ️ What does this chart show?"):
                st.markdown(
                    """
                    This donut chart shows the **market share** of the 8 largest cryptocurrencies by market cap.
                    - **Use case**: Understand how much of the top-8 basket each coin represents (e.g., BTC/ETH dominance).
                    """
                )

        # ===== 6️⃣ VOLATILITY RANKING (STD of 24H CHANGE) =====
        with st.container(border=True):
            st.subheader("⚔️ Volatility Ranking")
            volatility = (
                df_filtered.groupby("symbol")["change24h"]
                .std()
                .sort_values(ascending=False)
                .head(10)
            )
            fig6 = px.bar(
                x=volatility.values,
                y=volatility.index,
                orientation="h",
                color=volatility.values,
                color_continuous_scale="Reds",
                title="Top 10 Most Volatile Cryptocurrencies",
            )
            st.plotly_chart(fig6, use_container_width=True)
            with st.expander("ℹ️ What does this chart show?"):
                st.markdown(
                    """
                    This bar chart ranks the 10 most **volatile** cryptocurrencies using the standard deviation of
                    their 24h percentage change.
                    - **Interpretation**: Longer bars = larger fluctuations. Volatility implies potential upside and risk.
                    """
                )

        # ===== 7️⃣ TIME SERIES (IF MULTIPLE SNAPSHOTS) =====
        if df_filtered["timestamp"].nunique() > 1:
            with st.container(border=True):
                st.subheader("📅 Price Evolution Over Time")
                line_data = df_filtered[df_filtered["symbol"].isin(["BTC", "ETH", "SOL"])]
                fig7 = px.line(
                    line_data,
                    x="timestamp",
                    y="price",
                    color="symbol",
                    title="Price Evolution (BTC, ETH, SOL)",
                )
                st.plotly_chart(fig7, use_container_width=True)
                with st.expander("ℹ️ What does this chart show?"):
                    st.markdown(
                        """
                        This line chart shows **price evolution** over time for selected major cryptocurrencies.
                        - **Use case**: Observe trends, patterns, and volatility across scraping snapshots.
                        """
                    )

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
    unsafe_allow_html=True,
)

st.markdown("---")
st.caption("© 2025 | Streamlit - Plotly - Python")
