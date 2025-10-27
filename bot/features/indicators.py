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

    # --- Basic price and volatility ---
    df["ret1"] = df["close"].pct_change()
    df["vol"] = df["ret1"].rolling(20).std()
    df["ma_fast"] = df["close"].rolling(10).mean()
    df["ma_slow"] = df["close"].rolling(50).mean()
    df["ma_ratio"] = df["ma_fast"] / df["ma_slow"]

    # --- RSI and relative volume ---
    df["rsi"] = rsi(df["close"], 14)
    df["rvol"] = df["volume"] / df["volume"].rolling(50).mean()

    # --- EMA & MACD ---
    df["ema_fast"] = df["close"].ewm(span=12).mean()
    df["ema_slow"] = df["close"].ewm(span=26).mean()
    df["macd"] = df["ema_fast"] - df["ema_slow"]
    df["signal"] = df["macd"].ewm(span=9).mean()
    df["macd_hist"] = df["macd"] - df["signal"]

    # --- Momentum and ROC ---
    df["roc"] = df["close"].pct_change(12)
    df["momentum"] = df["close"] / df["close"].shift(10) - 1

    # --- ATR (Average True Range) ---
    df["tr"] = np.maximum(df["high"] - df["low"],
                          np.maximum(abs(df["high"] - df["close"].shift()),
                                     abs(df["low"] - df["close"].shift())))
    df["atr"] = df["tr"].rolling(14).mean()

    # --- Stochastic oscillator ---
    df["stoch_k"] = 100 * (df["close"] - df["low"].rolling(14).min()) / (
        df["high"].rolling(14).max() - df["low"].rolling(14).min()
    )
    df["stoch_d"] = df["stoch_k"].rolling(3).mean()

    # --- ADX (trend strength) ---
    up = df["high"].diff()
    down = -df["low"].diff()
    plus_dm = np.where((up > down) & (up > 0), up, 0.0)
    minus_dm = np.where((down > up) & (down > 0), down, 0.0)
    tr14 = df["tr"].rolling(14).sum()
    plus_di = 100 * (pd.Series(plus_dm).rolling(14).sum() / tr14)
    minus_di = 100 * (pd.Series(minus_dm).rolling(14).sum() / tr14)
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di + 1e-9)
    df["adx"] = dx.rolling(14).mean()

    # --- Money Flow Index ---
    tp = (df["high"] + df["low"] + df["close"]) / 3
    mf = tp * df["volume"]
    pos_mf = np.where(tp > tp.shift(1), mf, 0)
    neg_mf = np.where(tp < tp.shift(1), mf, 0)
    mfr = pd.Series(pos_mf).rolling(14).sum() / (
        pd.Series(neg_mf).rolling(14).sum() + 1e-9
    )
    df["mfi"] = 100 - (100 / (1 + mfr))

    # --- CCI (Commodity Channel Index) ---
    tp_mean = tp.rolling(20).mean()
    tp_std = tp.rolling(20).std()
    df["cci"] = (tp - tp_mean) / (0.015 * tp_std)

    # --- Final cleanup ---
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna().reset_index(drop=True)
    return df
