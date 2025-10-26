from sqlalchemy import create_engine, text
from bot import config

engine = create_engine(config.DB_URL, echo=False, future=True)

def init_db():
    with engine.begin() as con:
        con.execute(text("""
        CREATE TABLE IF NOT EXISTS candles (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          ts INTEGER NOT NULL,
          symbol TEXT NOT NULL,
          open REAL, high REAL, low REAL, close REAL, volume REAL,
          UNIQUE(ts, symbol)
        );
        """))
        con.execute(text("""
        CREATE TABLE IF NOT EXISTS signals (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          ts INTEGER NOT NULL,
          symbol TEXT NOT NULL,
          proba_up REAL NOT NULL,
          action TEXT NOT NULL
        );
        """))
        con.execute(text("""
        CREATE TABLE IF NOT EXISTS trades (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          ts_open INTEGER NOT NULL,
          ts_close INTEGER,
          symbol TEXT NOT NULL,
          side TEXT NOT NULL,
          qty REAL NOT NULL,
          entry REAL NOT NULL,
          exit REAL,
          pnl REAL
        );
        """))
        con.execute(text("""
        CREATE TABLE IF NOT EXISTS equity (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          ts INTEGER NOT NULL,
          equity REAL NOT NULL
        );
        """))
