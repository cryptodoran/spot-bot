import sqlite3
import pandas as pd
import os

# Path to your Downloads folder on D: drive
downloads_path = r"D:\Downloads"

# Ensure the folder exists
os.makedirs(downloads_path, exist_ok=True)

# Connect to your local trading database
con = sqlite3.connect("spotbot.db")

# === EXPORT TRADES ===
trades = pd.read_sql("SELECT * FROM trades ORDER BY ts_open ASC", con)
trades_file = os.path.join(downloads_path, "trades_export.csv")
trades.to_csv(trades_file, index=False)
print(f"✅ Exported {len(trades)} trades to {trades_file}")

# === EXPORT EQUITY (optional) ===
equity = pd.read_sql("SELECT * FROM equity ORDER BY ts ASC", con)
equity_file = os.path.join(downloads_path, "equity_export.csv")
equity.to_csv(equity_file, index=False)
print(f"✅ Exported {len(equity)} equity entries to {equity_file}")

con.close()
print("All exports complete.")
