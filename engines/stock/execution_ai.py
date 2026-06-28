import json
import os
from datetime import datetime

from engines.stock.portfolio_engine import PortfolioEngine
from engines.stock.history_engine import HistoryEngine
from engines.stock.trade_history_engine import TradeHistoryEngine

ROOT = r"C:\ARGOS_STOCK"

DECISION = os.path.join(ROOT, "data", "decision", "final_decision.json")
OUT = os.path.join(ROOT, "data", "execution", "execution_status.json")


class ExecutionAI:

    def now(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def load(self, path, default):
        if not os.path.exists(path):
            return default
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return default

    def save(self, path, data):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def run(self):

        portfolio = PortfolioEngine()
        history = HistoryEngine()
        trade_history = TradeHistoryEngine()

        decision = self.load(DECISION, {})

        signal = decision.get("signal", "WAIT")
        score = decision.get("score", 0)

        symbol = decision.get("symbol", "")
        price = float(decision.get("price", 0) or 0)

        action = "NO_ACTION"

        if signal == "BUY" and symbol and price > 0:
            if len(portfolio.positions) == 0:
                portfolio.add_position(
                    symbol,
                    "LONG",
                    price,
                    1
                )
                action = "PAPER_BUY"

        elif signal == "SELL" and symbol and price > 0:

            if len(portfolio.positions) > 0:

                p = portfolio.positions[0]

                trade_history.add_trade(
                    p["symbol"],
                    p["side"],
                    p["entry"],
                    price,
                    p["qty"],
                    "AI_EXIT"
                )

                portfolio.close_all()

                action = "PAPER_SELL"

        result = {
            "engine": "execution_ai",
            "status": "READY",
            "mode": "PAPER_ONLY",
            "signal": signal,
            "score": score,
            "action": action,
            "symbol": symbol,
            "price": price,
            "positions": len(portfolio.positions),
            "history": trade_history.run().get("total_trades", 0),
            "updated_at": self.now()
        }

        self.save(OUT, result)

        return result


def run():
    return ExecutionAI().run()


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))