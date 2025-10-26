import pandas as pd
from sqlalchemy import text
from bot.db import engine
from bot.features.indicators import build_features
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
import pickle

def load_candles():
    with engine.begin() as con:
        return pd.read_sql(text("SELECT ts, close, volume FROM candles ORDER BY ts"), con)

def prepare_dataset(df):
    feat = build_features(df)
    feat["y_up"] = (feat["close"].shift(-1) > feat["close"]).astype(int)
    feat = feat.dropna()
    X = feat[[
        "ret1", "vol", "ma_ratio", "rsi", "rvol",
        "ema_fast", "ema_slow", "macd", "signal", "macd_hist",
        "roc", "momentum", "macd_slope", "ma_distance"
    ]].values

    y = feat["y_up"].values
    return X, y

def train():
    df = load_candles()
    X, y = prepare_dataset(df)
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=6,
        random_state=42
    )
    model.fit(Xs, y)
    with open("model.pkl", "wb") as f:
        pickle.dump(model, f)
    with open("scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)
    print("Model trained and saved.")

if __name__ == "__main__":
    train()
