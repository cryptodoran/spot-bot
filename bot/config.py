from dotenv import load_dotenv
import os

load_dotenv()

EXCHANGE = os.getenv("EXCHANGE")
SYMBOL = os.getenv("SYMBOL")
TIMEFRAME = os.getenv("TIMEFRAME")
DB_URL = os.getenv("DB_URL")
STARTING_USD = float(os.getenv("STARTING_USD"))
MAX_TRADE_RISK_PCT = float(os.getenv("MAX_TRADE_RISK_PCT"))
LONG_THRESHOLD = float(os.getenv("LONG_THRESHOLD"))
FLAT_THRESHOLD = float(os.getenv("FLAT_THRESHOLD"))