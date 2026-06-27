import json
import os
from datetime import datetime

ROOT = r"C:\ARGOS_STOCK"

HISTORY = os.path.join(ROOT, "data", "portfolio", "history.json")
STATUS = os.path.join(ROOT, "data", "learning", "learning_status.json")


def load(path, default):
    if not os.path.exists(path):
        return default

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


class LearningEngine:

    def run(self):

        history = load(HISTORY, [])

        total = len(history)

        win = 0
        loss = 0

        win_sum = 0
        loss_sum = 0

        for trade in history:

            pnl = trade.get("pnl", 0)

            if pnl >= 0:
                win += 1
                win_sum += pnl
            else:
                loss += 1
                loss_sum += pnl

        win_rate = round((win / total) * 100, 2) if total else 0

        result = {
            "engine": "learning_engine",
            "status": "READY",
            "mode": "PAPER_ONLY",
            "total_trades": total,
            "wins": win,
            "losses": loss,
            "win_rate": win_rate,
            "average_win": round(win_sum / win, 2) if win else 0,
            "average_loss": round(loss_sum / loss, 2) if loss else 0,
            "learning_state": "COLLECTING" if total < 100 else "ANALYZING",
            "next_target": 100,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        save(STATUS, result)

        return result


if __name__ == "__main__":

    import pprint

    pprint.pp(LearningEngine().run())