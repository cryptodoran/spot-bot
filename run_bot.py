import time
from sqlalchemy import text
from bot.db import init_db, engine
from bot import config
from bot.data.collector import fetch_and_store_latest
from bot.models.inference import latest_proba
from bot.execution.paper_broker import PaperBroker
from bot.strategy.strategy import decide_action

def log_signal(ts, proba, action):
    with engine.begin() as con:
        con.execute(text("""
        INSERT INTO signals(ts,symbol,proba_up,action)
        VALUES(:ts,:s,:p,:a)
        """), dict(ts=ts, s=config.SYMBOL, p=proba, a=action))

def main():
    init_db()
    broker = PaperBroker()
    print("Coinbase paper bot running...")
    last_ts = None
    while True:
        try:
            fetch_and_store_latest()
            ts, price, p = latest_proba(config.SYMBOL)

            # only run logic if a new candle has appeared
            if ts != last_ts:
                action = decide_action(p)
                log_signal(ts, p, action)
                print(f"{config.SYMBOL} | Price: {price:.2f} | ProbUp: {p:.3f} | Action: {action}")

                if action == "LONG":
                    broker.buy(ts, price, risk_pct=config.MAX_TRADE_RISK_PCT)
                elif action == "CLOSE":
                    broker.close_all(ts, price)

                broker.mark_to_market(price)
                last_ts = ts  # update timestamp so it won't repeat the same candle

            time.sleep(10)


        except KeyboardInterrupt:
            print("Stopping bot, closing open positions...")
            try:
                broker.close_all(ts=None, price=None)
                print("All positions closed. Goodbye.")
            except Exception as e:
                print("Error while closing positions:", e)
            break
        except Exception as e:
            print("Error:", e)
            time.sleep(5)


if __name__ == "__main__":
    main()
