import json
import os
from datetime import datetime

ROOT = r"C:\ARGOS_STOCK"

ACCOUNT = os.path.join(ROOT, "data", "portfolio", "account.json")
TRADE_HISTORY = os.path.join(ROOT, "data", "trade", "trade_history.json")


def load(path, default):
    if not os.path.exists(path):
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


class PnLEngine:

    def now(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def run(self):

        account = load(ACCOUNT, {})
        trade_data = load(TRADE_HISTORY, {"trades": []})
        trades_list = trade_data.get("trades", [])

        total_pnl = round(sum(float(t.get("pnl", 0) or 0) for t in trades_list), 2)
        win = len([t for t in trades_list if float(t.get("pnl", 0) or 0) > 0])
        loss = len([t for t in trades_list if float(t.get("pnl", 0) or 0) < 0])
        trades = len(trades_list)

        win_rate = 0
        if trades > 0:
            win_rate = round((win / trades) * 100, 2)

        base_cash = float(account.get("initial_cash", 10000000) or 10000000)
        cash = round(base_cash + total_pnl, 2)
        equity = cash

        return {
            "engine": "pnl_engine",
            "status": "READY",
            "mode": "PAPER_ONLY",
            "cash": cash,
            "equity": equity,
            "today_pnl": total_pnl,
            "total_pnl": total_pnl,
            "win": win,
            "loss": loss,
            "trades": trades,
            "win_rate": win_rate,
            "history_count": trades,
            "updated_at": self.now()
        }


if __name__ == "__main__":
    import pprint
    pprint.pp(PnLEngine().run())