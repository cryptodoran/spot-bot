import pandas as pd
from sqlalchemy import text
from bot.db import engine
from bot.features.indicators import build_features
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
import pickle
from xgboost import XGBClassifier

def load_candles():
    with engine.begin() as con:
        return pd.read_sql(
            text("SELECT ts, open, high, low, close, volume FROM candles ORDER BY ts"),
            con
        )

def prepare_dataset(df):
    feat = build_features(df)
    feat["y_up"] = (feat["close"].shift(-1) > feat["close"]).astype(int)
    feat = feat.dropna()
    X = feat[[
        "ret1", "vol", "ma_ratio", "rsi", "rvol",
        "ema_fast", "ema_slow", "macd", "signal", "macd_hist",
        "roc", "momentum", "atr", "stoch_k", "stoch_d",
        "adx", "mfi", "cci"
    ]].values
    y = feat["y_up"].values
    return X, y

def train():
    df = load_candles()
    X, y = prepare_dataset(df)
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)
    model = XGBClassifier(
        n_estimators=500,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        tree_method="hist"
    )
    model.fit(Xs, y)
    with open("model.pkl", "wb") as f:
        pickle.dump(model, f)
    with open("scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)
    print("Model trained and saved.")

if __name__ == "__main__":
    train()
