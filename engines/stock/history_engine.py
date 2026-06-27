import json
import os
from datetime import datetime

ROOT = r"C:\ARGOS_STOCK"

HISTORY = os.path.join(ROOT, "data", "portfolio", "history.json")


def load():
    if not os.path.exists(HISTORY):
        return []

    with open(HISTORY, "r", encoding="utf-8") as f:
        return json.load(f)


class HistoryEngine:

    def run(self):

        history = load()

        total = len(history)

        win = sum(1 for x in history if x.get("pnl", 0) >= 0)
        loss = total - win

        total_pnl = sum(x.get("pnl", 0) for x in history)

        avg = round(total_pnl / total, 2) if total else 0

        last = history[-1] if total else {}

        return {
            "engine": "history_engine",
            "status": "READY",
            "total_trades": total,
            "wins": win,
            "losses": loss,
            "total_pnl": total_pnl,
            "average_pnl": avg,
            "last_trade": last,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


if __name__ == "__main__":

    import pprint

    pprint.pp(HistoryEngine().run())