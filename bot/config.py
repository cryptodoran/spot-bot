from dotenv import load_dotenv
import os

load_dotenv()

EXCHANGE = os.getenv("EXCHANGE", "coinbase")
SYMBOL = os.getenv("SYMBOL", "BTC/USD")
TIMEFRAME = os.getenv("TIMEFRAME", "1m")
DB_URL = os.getenv("DB_URL", "sqlite:///./spotbot.db")
STARTING_USD = float(os.getenv("STARTING_USD", "10000"))
MAX_TRADE_RISK_PCT = float(os.getenv("MAX_TRADE_RISK_PCT", "1.0"))
LONG_THRESHOLD = float(os.getenv("LONG_THRESHOLD", "0.53"))
FLAT_THRESHOLD = float(os.getenv("FLAT_THRESHOLD", "0.47"))