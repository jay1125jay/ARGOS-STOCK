import json
import os
from datetime import datetime

ROOT = r"C:\ARGOS_STOCK"

ACCOUNT = os.path.join(ROOT, "data", "portfolio", "account.json")
HISTORY = os.path.join(ROOT, "data", "portfolio", "history.json")


def load(path, default):
    if not os.path.exists(path):
        return default

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class PnLEngine:

    def run(self):

        account = load(ACCOUNT, {})
        history = load(HISTORY, [])

        total = account.get("total_pnl", 0)
        today = account.get("today_pnl", 0)

        win = account.get("win", 0)
        loss = account.get("loss", 0)

        trades = win + loss

        if trades == 0:
            win_rate = 0
        else:
            win_rate = round((win / trades) * 100, 2)

        return {
            "engine": "pnl_engine",
            "status": "READY",
            "cash": account.get("cash", 0),
            "equity": account.get("equity", 0),
            "today_pnl": today,
            "total_pnl": total,
            "win": win,
            "loss": loss,
            "trades": trades,
            "win_rate": win_rate,
            "history_count": len(history),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


if __name__ == "__main__":

    import pprint

    pprint.pp(PnLEngine().run())