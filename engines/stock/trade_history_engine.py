import json
import os
from datetime import datetime

ROOT = r"C:\ARGOS_STOCK"

OUT = os.path.join(ROOT, "data", "trade", "trade_history.json")


class TradeHistoryEngine:

    def now(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def load(self):
        if not os.path.exists(OUT):
            return {
                "engine": "trade_history_engine",
                "mode": "PAPER_ONLY",
                "trades": []
            }

        try:
            with open(OUT, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {
                "engine": "trade_history_engine",
                "mode": "PAPER_ONLY",
                "trades": []
            }

    def save(self, data):
        os.makedirs(os.path.dirname(OUT), exist_ok=True)

        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add_trade(self, symbol, side, entry, exit_price, qty, reason):
        data = self.load()
        trades = data.get("trades", [])

        entry = float(entry or 0)
        exit_price = float(exit_price or 0)
        qty = int(qty or 0)

        pnl = 0
        if side == "LONG":
            pnl = round((exit_price - entry) * qty, 2)

        trade = {
            "symbol": symbol,
            "side": side,
            "entry": entry,
            "exit": exit_price,
            "qty": qty,
            "pnl": pnl,
            "reason": reason,
            "closed_at": self.now()
        }

        trades.append(trade)

        data["trades"] = trades
        data["total_trades"] = len(trades)
        data["total_pnl"] = sum(float(t.get("pnl", 0)) for t in trades)
        data["updated_at"] = self.now()

        self.save(data)

        return trade

    def run(self):
        data = self.load()
        trades = data.get("trades", [])

        total_pnl = sum(float(t.get("pnl", 0)) for t in trades)
        wins = len([t for t in trades if float(t.get("pnl", 0)) > 0])
        losses = len([t for t in trades if float(t.get("pnl", 0)) < 0])

        return {
            "engine": "trade_history_engine",
            "status": "READY",
            "mode": "PAPER_ONLY",
            "total_trades": len(trades),
            "wins": wins,
            "losses": losses,
            "total_pnl": round(total_pnl, 2),
            "updated_at": self.now()
        }


def run():
    return TradeHistoryEngine().run()


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))