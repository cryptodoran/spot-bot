import pandas as pd
import numpy as np

def rsi(series: pd.Series, period: int = 14):
    delta = series.diff()
    up = np.where(delta > 0, delta, 0.0)
    down = np.where(delta < 0, -delta, 0.0)
    roll_up = pd.Series(up).rolling(period).mean()
    roll_down = pd.Series(down).rolling(period).mean()
    rs = roll_up / (roll_down + 1e-9)
    return 100 - (100 / (1 + rs))

def build_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values("ts").copy()
    df["ret1"] = df["close"].pct_change()
    df["vol"] = df["ret1"].rolling(20).std().fillna(0)
    df["ma_fast"] = df["close"].rolling(10).mean()
    df["ma_slow"] = df["close"].rolling(50).mean()
    df["ma_ratio"] = df["ma_fast"] / df["ma_slow"]
    df["rsi"] = rsi(df["close"], 14)
    df["rvol"] = df["volume"] / df["volume"].rolling(50).mean()

    # --- Extra trend and momentum indicators ---
    df["ema_fast"] = df["close"].ewm(span=12).mean()
    df["ema_slow"] = df["close"].ewm(span=26).mean()
    df["macd"] = df["ema_fast"] - df["ema_slow"]
    df["signal"] = df["macd"].ewm(span=9).mean()
    df["macd_hist"] = df["macd"] - df["signal"]

    df["roc"] = df["close"].pct_change(12)
    df["momentum"] = df["close"] / df["close"].shift(10) - 1

    # Trend slope and crossover distance
    df["macd_slope"] = df["macd"].diff()
    df["ma_distance"] = (df["ma_fast"] - df["ma_slow"]) / df["ma_slow"]
    # --- Extra volatility and momentum features ---
    df["ema_diff"] = df["ema_fast"] - df["ema_slow"]
    df["rsi_change"] = df["rsi"].diff()

    # simple 14-period price range as a crude ATR proxy
    df["atr"] = df["high"].rolling(14).max() - df["low"].rolling(14).min()

    # Bollinger bands (20-period)
    mid = df["close"].rolling(20).mean()
    std = df["close"].rolling(20).std()
    df["boll_up"] = mid + 2 * std
    df["boll_down"] = mid - 2 * std
    df["boll_width"] = df["boll_up"] - df["boll_down"]

    return df.dropna()
