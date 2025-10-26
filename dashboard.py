import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text
from bot.db import engine
from bot import config

st.set_page_config(page_title="Coinbase Paper Bot", layout="wide")
st.title("Coinbase Paper Trading Dashboard")

@st.cache_data(ttl=5)
def get_table(name):
    with engine.begin() as con:
        return pd.read_sql(text(f"SELECT * FROM {name} ORDER BY ts"), con)

candles = get_table("candles")
signals = get_table("signals")
equity = get_table("equity")

col1, col2 = st.columns(2)
with col1:
    st.subheader("BTC/USD Price")
    if not candles.empty:
        st.plotly_chart(px.line(candles, x="ts", y="close"), use_container_width=True)
with col2:
    st.subheader("Model Probability")
    if not signals.empty:
        st.plotly_chart(px.line(signals, x="ts", y="proba_up"), use_container_width=True)

st.subheader("Equity Curve")
if not equity.empty:
    st.plotly_chart(px.line(equity, x="ts", y="equity"), use_container_width=True)

st.subheader("Recent Signals")
if not signals.empty:
    st.dataframe(signals.tail(20).iloc[::-1], use_container_width=True)
