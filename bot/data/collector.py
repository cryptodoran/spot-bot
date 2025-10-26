import time
import ccxt
import pandas as pd
from sqlalchemy import create_engine, text
from bot import config

# --- Database connection ---
engine = create_engine(config.DB_URL)

# --- Get exchange connection ---
def get_exchange():
    ex = getattr(ccxt, config.EXCHANGE)({
        "enableRateLimit": True,
    })
    return ex


# --- Fetch recent OHLCV candles and store them ---
def fetch_and_store_latest():
    ex = get_exchange()
    data = ex.fetch_ohlcv(config.SYMBOL, timeframe=config.TIMEFRAME, limit=2)
    if not data:
        return
    ts, o, h, l, c, v = data[-1]
    with engine.begin() as con:
        con.execute(text("""
            INSERT OR IGNORE INTO candles(ts, symbol, open, high, low, close, volume)
            VALUES(:ts, :symbol, :o, :h, :l, :c, :v)
        """), dict(ts=ts, symbol=config.SYMBOL, o=o, h=h, l=l, c=c, v=v))


# --- Backfill large historical dataset ---
def backfill(total_to_fetch=40000):
    """
    total_to_fetch = number of candles to download
    40,000 5m candles ≈ 139 days
    """
    ex = get_exchange()
    print(f"Fetching {total_to_fetch} {config.TIMEFRAME} candles from {config.EXCHANGE} for {config.SYMBOL}...")

    limit_per_call = 1000  # ccxt limit
    since = ex.milliseconds() - total_to_fetch * 5 * 60_000  # go back total_to_fetch * 5m
    fetched = 0

    while fetched < total_to_fetch:
        data = ex.fetch_ohlcv(config.SYMBOL, timeframe=config.TIMEFRAME, since=since, limit=limit_per_call)
        if not data:
            break
        with engine.begin() as con:
            for ts, o, h, l, c, v in data:
                con.execute(text("""
                    INSERT OR IGNORE INTO candles(ts, symbol, open, high, low, close, volume)
                    VALUES(:ts, :symbol, :o, :h, :l, :c, :v)
                """), dict(ts=ts, symbol=config.SYMBOL, o=o, h=h, l=l, c=c, v=v))
        since = min(data[-1][0] + 5 * 60_000, ex.milliseconds() - 5 * 60_000)
        fetched += len(data)
        print(f"Fetched {fetched}/{total_to_fetch} candles...")
        time.sleep(1)  # be nice to Coinbase

    print("✅ Backfill complete.")


# --- Main execution ---
if __name__ == "__main__":
    # Adjust this to how much history you want
    backfill(total_to_fetch=40000)

    print("Starting live collector...")
    while True:
        try:
            fetch_and_store_latest()
            time.sleep(10)
        except KeyboardInterrupt:
            print("Stopped.")
            break
        except Exception as e:
            print("Error:", e)
            time.sleep(5)
