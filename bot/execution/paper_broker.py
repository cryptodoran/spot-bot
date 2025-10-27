import pandas as pd
import time
from sqlalchemy import text
from bot.db import engine


class PaperBroker:
    def __init__(self, starting_balance=10000.0):
        self.balance = starting_balance
        self.positions = []  # list of open positions
        self.trades = []     # closed trades

    def buy(self, ts, price, qty=None, risk_pct=1.0, symbol="BTC/USD"):
        """Open a long position"""
        if price is None:
            print("Cannot execute buy — price is None.")
            return

        if qty is None:
            qty = (self.balance * (risk_pct / 100)) / price

        pos = {
            "ts_open": ts,
            "symbol": symbol,
            "side": "LONG",
            "qty": qty,
            "entry": price
        }
        self.positions.append(pos)

        # Save trade to DB
        with engine.begin() as con:
            con.execute(text("""
                INSERT INTO trades (ts_open, symbol, side, qty, entry)
                VALUES (:ts_open, :symbol, :side, :qty, :entry)
            """), dict(
                ts_open=ts,
                symbol=symbol,
                side="LONG",
                qty=qty,
                entry=price
            ))

        print(f"Opened LONG at {price:.2f}, qty={qty:.6f}")

    def close_all(self, ts, price):
        """Close all open positions"""
        if not hasattr(self, "positions"):
            self.positions = []

        if price is None:
            print("Cannot close positions — price is None.")
            return

        if not self.positions:
            print("No open positions to close.")
            return

        for pos in list(self.positions):
            qty = pos.get("qty")
            entry = pos.get("entry")
            side = pos.get("side")
            symbol = pos.get("symbol", "BTC/USD")

            if qty is None or entry is None:
                print("Skipping invalid position:", pos)
                continue

            pnl = (price - entry) * qty if side == "LONG" else (entry - price) * qty
            self.balance += pnl

            self.trades.append({
                "ts_open": pos["ts_open"],
                "ts_close": ts,
                "symbol": symbol,
                "side": side,
                "qty": qty,
                "entry": entry,
                "exit": price,
                "pnl": pnl
            })

            # --- Update DB record for this trade ---
            with engine.begin() as con:
                con.execute(text("""
                    UPDATE trades
                    SET ts_close = :ts_close,
                        exit = :exit,
                        pnl = :pnl
                    WHERE ts_open = :ts_open
                """), dict(
                    ts_close=ts,
                    exit=price,
                    pnl=pnl,
                    ts_open=pos["ts_open"]
                ))

    def mark_to_market(self, price):
        """Update open trade unrealized PnL (optional)"""
        if not self.positions:
            return

        total_pnl = 0
        for pos in self.positions:
            entry = pos["entry"]
            qty = pos["qty"]
            side = pos["side"]
            pnl = (price - entry) * qty if side == "LONG" else (entry - price) * qty
            total_pnl += pnl

        print(f"Mark-to-market unrealized PnL: {total_pnl:.2f}")

    def export_trades(self, path="D:/Downloads/paper_trades.csv"):
        """Save all closed trades to CSV"""
        if not self.trades:
            print("No trades to export.")
            return

        df = pd.DataFrame(self.trades)
        df.to_csv(path, index=False)
        print(f"Trades exported to {path}")

