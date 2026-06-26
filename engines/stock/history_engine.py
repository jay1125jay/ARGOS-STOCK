import json
import os
from datetime import datetime

ROOT = r"C:\ARGOS_STOCK"

HISTORY = os.path.join(ROOT, "data", "history", "trade_history.json")


def ensure():
    os.makedirs(os.path.dirname(HISTORY), exist_ok=True)


def load():
    if not os.path.exists(HISTORY):
        return []

    try:
        with open(HISTORY, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save(data):
    with open(HISTORY, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


class HistoryEngine:

    def __init__(self):
        ensure()
        self.history = load()

    def add_trade(
        self,
        symbol,
        side,
        entry,
        exit_price,
        qty,
        pnl,
        reason
    ):

        self.history.append({

            "symbol": symbol,
            "side": side,

            "entry": entry,
            "exit": exit_price,

            "qty": qty,

            "pnl": pnl,

            "reason": reason,

            "closed_at":
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        })

        save(self.history)

    def get_all(self):
        return self.history

    def clear(self):
        self.history = []
        save(self.history)


if __name__ == "__main__":

    h = HistoryEngine()

    print("=" * 60)
    print("HISTORY ENGINE")
    print("TRADES :", len(h.get_all()))
    print("READY")