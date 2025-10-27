import pickle
import pandas as pd
from sqlalchemy import create_engine, text
from bot import config
from bot.features.indicators import build_features

# --- Load model and scaler ---
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

with open("scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

# --- Database connection ---
engine = create_engine(config.DB_URL)

def latest_proba(symbol: str):
    with engine.begin() as con:
        df = pd.read_sql(text("SELECT ts, open, high, low, close, volume FROM candles WHERE symbol=:s ORDER BY ts"), con, params={"s": symbol})
    feat = build_features(df).tail(1)
    if feat.empty:
        raise ValueError("No valid feature rows found — need more candles or check indicator logic.")

    X = feat[[
        "ret1", "vol", "ma_ratio", "rsi", "rvol",
        "ema_fast", "ema_slow", "macd", "signal", "macd_hist",
        "roc", "momentum", "atr", "stoch_k", "stoch_d",
        "adx", "mfi", "cci"
    ]].values

    p = model.predict_proba(scaler.transform(X))[0, 1]
    return df["ts"].iloc[-1], df["close"].iloc[-1], p

def log_signal(ts, price, proba, action, symbol="BTC/USD"):
    with engine.begin() as con:
        con.execute(text("""
            INSERT INTO signals (ts, symbol, price, proba_up, action)
            VALUES (:ts, :symbol, :price, :proba_up, :action)
        """), dict(
            ts=ts,
            symbol=symbol,
            price=price,
            proba_up=proba,
            action=action
        ))

