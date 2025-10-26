from dataclasses import dataclass
from sqlalchemy import text
from bot.db import engine
from bot import config
import time

@dataclass
class Portfolio:
    usd: float
    asset_qty: float

class PaperBroker:
    def __init__(self):
        self.pf = Portfolio(usd=config.STARTING_USD, asset_qty=0.0)

    def mark_to_market(self, price):
        equity = self.pf.usd + self.pf.asset_qty * price
        with engine.begin() as con:
            con.execute(text("INSERT INTO equity(ts,equity) VALUES(:ts,:eq)"),
                        dict(ts=int(time.time()*1000), eq=equity))
        return equity

    def buy(self, ts, price, risk_pct):
        risk_usd = self.pf.usd * (risk_pct / 100)
        qty = risk_usd / price
        cost = qty * price
        if cost > self.pf.usd:
            cost = self.pf.usd
            qty = cost / price
        self.pf.usd -= cost
        self.pf.asset_qty += qty
        with engine.begin() as con:
            con.execute(text("""
            INSERT INTO trades(ts_open, symbol, side, qty, entry)
            VALUES(:ts,:sym,'LONG',:qty,:entry)
            """), dict(ts=ts, sym=config.SYMBOL, qty=qty, entry=price))
        return qty

    def close_all(self, ts, price):
        qty = self.pf.asset_qty
        if qty <= 0:
            return
        proceeds = qty * price
        self.pf.usd += proceeds
        self.pf.asset_qty = 0
        with engine.begin() as con:
            trade = con.execute(text(
                "SELECT id, entry FROM trades WHERE ts_close IS NULL ORDER BY id DESC LIMIT 1"
            )).mappings().first()
            if trade:
                pnl = proceeds - (qty * trade["entry"])
                con.execute(text("""
                    UPDATE trades SET ts_close=:tsc, exit=:ex, pnl=:p WHERE id=:i
                """), dict(tsc=ts, ex=price, p=pnl, i=trade["id"]))
