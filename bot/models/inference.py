import pickle
import pandas as pd
from sqlalchemy import text
from bot.db import engine
from bot.features.indicators import build_features

with open("model.pkl", "rb") as f:
    MODEL = pickle.load(f)
with open("scaler.pkl", "rb") as f:
    SCALER = pickle.load(f)

def latest_proba(symbol: str):
    with engine.begin() as con:
        df = pd.read_sql(text("SELECT ts, close, volume FROM candles WHERE symbol=:s ORDER BY ts"),
                         con, params={"s": symbol})
    feat = build_features(df).tail(1)
    X = feat[[
        "ret1", "vol", "ma_ratio", "rsi", "rvol",
        "ema_fast", "ema_slow", "macd", "signal", "macd_hist",
        "roc", "momentum",
        "macd_slope", "ma_distance"
    ]].values
    Xs = SCALER.transform(X)
    prob_up = float(MODEL.predict_proba(Xs)[0,1])
    ts = int(feat["ts"].iloc[0])
    price = float(feat["close"].iloc[0])
    return ts, price, prob_up
