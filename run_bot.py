import time
import numpy as np
from sqlalchemy import text
from bot.db import init_db, engine
from bot import config
from bot.data.collector import fetch_and_store_latest
from bot.execution.paper_broker import PaperBroker
from bot.strategy.strategy import decide_action
from bot.models.inference import latest_proba, log_signal


def main():
    init_db()
    broker = PaperBroker()
    print("Coinbase paper bot running...")

    last_ts = None

    while True:
        try:
            fetch_and_store_latest()
            ts, price, p = latest_proba(config.SYMBOL)

            # Run logic only when a new candle appears
            if ts != last_ts:
                action = decide_action(p)

                # Log the signal (timestamp, price, proba, action)
                log_signal(ts, price, p, action, config.SYMBOL)

                print(f"{config.SYMBOL} | Price: {price:.2f} | ProbUp: {p:.3f} | Action: {action}")

                # Execute the simulated trade
                if action == "LONG":
                    broker.buy(ts, price)
                elif action == "CLOSE":
                    broker.close_all(ts, price)

                # Mark unrealized PnL for any open trades
                broker.mark_to_market(price)

                last_ts = ts  # prevent duplicate actions for same candle

            # Wait for next candle (currently 1 minute)
            time.sleep(60)

        except KeyboardInterrupt:
            print("Stopping bot, closing open positions...")
            try:
                if 'price' in locals() and price is not None:
                    broker.close_all(int(time.time() * 1000), price)
                else:
                    print("No valid price found — skipping forced close.")
            except Exception as e:
                print("Error while closing positions:", e)
            print("Bot stopped cleanly.")
            break

        except Exception as e:
            print("Error:", e)
            time.sleep(10)


if __name__ == "__main__":
    main()
