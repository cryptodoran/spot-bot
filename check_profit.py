import sqlite3
import pandas as pd

# --- Connect to your database ---
con = sqlite3.connect("spotbot.db")

# --- Read all trades ---
trades = pd.read_sql("""
    SELECT 
        id,
        ts_open,
        ts_close,
        symbol,
        side,
        qty,
        entry,
        exit,
        pnl
    FROM trades
    ORDER BY ts_open DESC
""", con)

con.close()

# --- Clean up byte timestamps ---
def decode_ts(x):
    if isinstance(x, (bytes, bytearray)):
        try:
            return int.from_bytes(x, "little")
        except Exception:
            return None
    return x

trades["ts_open"] = trades["ts_open"].apply(decode_ts)
trades["ts_close"] = trades["ts_close"].apply(decode_ts)

# --- Convert timestamps to readable datetimes ---
trades["ts_open"] = pd.to_datetime(trades["ts_open"], unit="ms", errors="coerce")
trades["ts_close"] = pd.to_datetime(trades["ts_close"], unit="ms", errors="coerce")

# --- Fill missing pnl with 0 (for open trades) ---
trades["pnl"] = trades["pnl"].fillna(0)

# --- Display the last 10 trades ---
print("\n--- LAST 10 TRADES ---")
print(trades.head(10).to_string(index=False))

# --- Display total profit across all trades ---
total_profit = round(trades["pnl"].sum(), 2)
print("\n--- TOTAL PROFIT (USD) ---")
print(total_profit)

# --- Export to CSV for Excel ---
output_path = r"D:\Downloads\trade_history.csv"
trades.to_csv(output_path, index=False)
print(f"\n✅ Trade history exported to: {output_path}")
