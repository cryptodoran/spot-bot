import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sqlalchemy import text
from bot.db import engine

# --- Streamlit setup ---
st.set_page_config(page_title="Coinbase Paper Bot", layout="wide")
st.title("Coinbase Paper Trading Dashboard")

# --- Cached data loader ---
@st.cache_data(ttl=10)
def get_table(name):
    try:
        with engine.begin() as con:
            df = pd.read_sql(text(f"SELECT * FROM {name} ORDER BY ts"), con)
    except Exception:
        return pd.DataFrame()

    # Decode bytes if present
    def safe_decode(x):
        if isinstance(x, (bytes, bytearray)):
            try:
                return x.decode("utf-8")
            except Exception:
                return str(x)
        return x

    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].apply(safe_decode)

    # Convert timestamps
    if "ts" in df.columns:
        df["ts"] = pd.to_datetime(df["ts"], unit="ms", errors="coerce")

    df = df.replace([np.inf, -np.inf], np.nan).dropna(subset=["ts"])
    return df


# --- Load tables ---
candles = get_table("candles")
signals = get_table("signals")
equity = get_table("equity")

# --- Clean and rename signal columns ---
if not signals.empty:
    for col in ["symbol", "action"]:
        if col in signals.columns:
            signals[col] = signals[col].astype(str).str.replace("<bound method.*>", "", regex=True).str.strip()

    signals = signals.rename(columns={
        "ts": "Timestamp",
        "symbol": "Pair",
        "price": "Price",
        "proba_up": "Model Confidence",
        "action": "Action"
    })

# --- Charts ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("BTC/USD Price")
    if not candles.empty:
        st.plotly_chart(px.line(candles, x="ts", y="close", title="Price Chart"), use_container_width=True)
    else:
        st.warning("No candle data found in database.")

with col2:
    st.subheader("Model Probability")
    if not signals.empty:
        fig = px.line(signals, x="Timestamp", y="Model Confidence", title="Model Confidence vs Price")
        fig.add_scatter(
            x=signals["Timestamp"],
            y=signals["Price"],
            mode="lines",
            name="BTC/USD Price",
            yaxis="y2"
        )
        fig.update_layout(
            yaxis=dict(title="Model Confidence"),
            yaxis2=dict(title="BTC/USD Price", overlaying="y", side="right")
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No signal data found yet.")

st.subheader("Equity Curve")
if not equity.empty:
    st.plotly_chart(px.line(equity, x="ts", y="equity", title="Equity Curve"), use_container_width=True)
else:
    st.info("Equity data will appear once trades have been executed.")

# --- Recent signals table ---
st.subheader("Recent Model Outputs")
if not signals.empty:
    cols_to_show = ["Timestamp", "Pair", "Price", "Model Confidence", "Action"]
    st.dataframe(signals[cols_to_show].tail(20).iloc[::-1], use_container_width=True)
else:
    st.info("No recent signals available.")
