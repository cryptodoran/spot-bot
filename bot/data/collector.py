import time
import pandas as pd
from sqlalchemy import text
import ccxt
from bot import config
from bot.db import engine

last_ts = None  # Track last candle timestamp

def get_exchange():
    return getattr(ccxt, config.EXCHANGE)({"enableRateLimit": True})

def fetch_and_store_latest():
    global last_ts
    ex = get_exchange()
    try:
        data = ex.fetch_ohlcv(config.SYMBOL, timeframe=config.TIMEFRAME, limit=2)
    except Exception as e:
        print(f"⚠️ Fetch failed for {config.SYMBOL}: {e}")
        return

    if not data:
        print(f"⚠️ No data returned for {config.SYMBOL}.")
        return

    ts, o, h, l, c, v = data[-1]

    # ✅ Skip duplicate candles
    if ts == last_ts:
        print(f"⏸ No new candle yet for {config.SYMBOL}. Waiting...")
        return

    last_ts = ts
    print(f"📊 New candle detected for {config.SYMBOL}...")

    with engine.begin() as con:
        con.execute(text("""
            INSERT OR IGNORE INTO candles(ts, symbol, open, high, low, close, volume)
            VALUES(:ts, :symbol, :o, :h, :l, :c, :v)
        """), dict(ts=ts, symbol=config.SYMBOL, o=o, h=h, l=l, c=c, v=v))

    print(f"✅ Inserted {config.SYMBOL} candle at {pd.to_datetime(ts, unit='ms')}")


if __name__ == "__main__":
    print("Starting live collector...")
    while True:
        try:
            fetch_and_store_latest()
            time.sleep(60)  # check every minute for a new candle
        except KeyboardInterrupt:
            print("Stopped.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)
