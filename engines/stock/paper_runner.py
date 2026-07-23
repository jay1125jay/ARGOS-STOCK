import json
import os
import time
from datetime import datetime

from engines.stock.data_hub import DataHub
from engines.stock.chief_ai import ChiefAI
from engines.stock.decision_center import DecisionCenter
from engines.stock.portfolio_engine import PortfolioEngine
from engines.stock.trade_history_engine import TradeHistoryEngine

ROOT = r"C:\ARGOS_STOCK"
RUNNER_STATUS = os.path.join(ROOT, "data", "runner", "runner_status.json")
KIS_CACHE = os.path.join(ROOT, "data", "stock", "kis_cache.json")


class PaperRunner:

    def __init__(self):
        self.datahub = DataHub()
        self.chief = ChiefAI()
        self.decision = DecisionCenter()
        self.portfolio = PortfolioEngine()
        self.trade_history = TradeHistoryEngine()
        self.running = False

    def now(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def load_json(self, path, default):
        if not os.path.exists(path):
            return default
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default

    def get_quote_map(self):
        cache = self.load_json(KIS_CACHE, {})
        quotes = cache.get("quotes", [])
        return {
            q.get("symbol"): q
            for q in quotes
            if q.get("status") == "QUOTE_OK"
        }

    def get_best_symbol(self, ai):
        technical = ai.get("modules", {}).get("technical", {})
        symbol = technical.get("best_symbol", "")
        return symbol

    def get_price(self, symbol):
        qmap = self.get_quote_map()
        q = qmap.get(symbol, {})
        return float(q.get("price", 0) or 0)

    def manage_positions(self):
        qmap = self.get_quote_map()
        closed = []

        for pos in list(self.portfolio.positions):
            symbol = pos.get("symbol", "")
            quote = qmap.get(symbol, {})
            price = float(quote.get("price", 0) or 0)

            if price <= 0:
                continue

            tp = float(pos.get("tp", 0) or 0)
            sl = float(pos.get("sl", 0) or 0)

            if tp and price >= tp:
                trade = self.portfolio.close_position(pos, price, "TP")
                self.trade_history.add_trade(
                    trade["symbol"],
                    trade["side"],
                    trade["entry"],
                    trade["exit"],
                    trade["qty"],
                    trade["pnl"],
                    trade["reason"]
                )
                closed.append(trade)

            elif sl and price <= sl:
                trade = self.portfolio.close_position(pos, price, "SL")
                self.trade_history.add_trade(
                    trade["symbol"],
                    trade["side"],
                    trade["entry"],
                    trade["exit"],
                    trade["qty"],
                    trade["pnl"],
                    trade["reason"]
                )
                closed.append(trade)

        return closed

    def try_entry(self, ai, decision):
        if decision.get("signal") != "BUY":
            return None

        if self.portfolio.has_position():
            return None

        symbol = self.get_best_symbol(ai)
        if not symbol:
            return None

        price = self.get_price(symbol)
        if price <= 0:
            return None

        cash = float(self.portfolio.account.get("cash", 0) or 0)
        budget = min(cash * 0.1, 1000000)
        qty = int(budget // price)

        if qty <= 0:
            return None

        ok = self.portfolio.add_position(
            symbol=symbol,
            side="BUY",
            price=price,
            qty=qty,
            reason="DECISION_BUY"
        )

        if not ok:
            return None

        return {
            "symbol": symbol,
            "side": "BUY",
            "entry": price,
            "qty": qty,
            "reason": "DECISION_BUY",
            "opened_at": self.now()
        }

    def heartbeat(self, ai, decision, entry=None, closed=None):
        os.makedirs(os.path.dirname(RUNNER_STATUS), exist_ok=True)

        data = {
            "project": "ARGOS_STOCK",
            "engine": "PaperRunner",
            "mode": "PAPER_ONLY",
            "running": self.running,
            "real_order": False,
            "api_order": False,
            "auto_real_order": False,
            "ai_signal": ai.get("signal", "WAIT"),
            "final_signal": decision.get("signal", "WAIT"),
            "decision_score": decision.get("score", 0),
            "account": self.portfolio.account.get("cash", 0),
            "positions": len(self.portfolio.positions),
            "history": self.trade_history.run().get("total_trades", 0),
            "entry": entry,
            "closed": closed or [],
            "updated_at": self.now()
        }

        with open(RUNNER_STATUS, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return data

    def loop(self):
        self.datahub.save()

        closed = self.manage_positions()

        ai = self.chief.decide()
        decision = self.decision.evaluate(ai)

        entry = self.try_entry(ai, decision)

        status = self.heartbeat(ai, decision, entry, closed)

        print("=" * 60)
        print("ARGOS STOCK PAPER")
        print("MODE : PAPER_ONLY")
        print("REAL_ORDER : FALSE")
        print("API_ORDER : FALSE")
        print("AUTO_REAL_ORDER : FALSE")
        print("-" * 60)
        print("AI :", ai.get("signal", "WAIT"))
        print("FINAL :", decision.get("signal", "WAIT"))
        print("SCORE :", decision.get("score", 0))
        print("ACCOUNT :", self.portfolio.account.get("cash", 0))
        print("POSITION :", len(self.portfolio.positions))
        print("HISTORY :", self.trade_history.run().get("total_trades", 0))

        if entry:
            print("ENTRY :", entry)

        if closed:
            print("CLOSED :", closed)

        return status

    def once(self):
        self.running = False
        return self.loop()

    def start(self):
        print("PAPER RUNNER START")
        self.running = True

        while True:
            self.loop()
            time.sleep(3)


if __name__ == "__main__":
    result = PaperRunner().once()
    print(json.dumps(result, indent=2, ensure_ascii=False))