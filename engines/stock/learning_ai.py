import json
import os
from datetime import datetime

ROOT = r"C:\ARGOS_STOCK"

HISTORY = os.path.join(ROOT, "data", "history", "trade_history.json")
OUT = os.path.join(ROOT, "data", "learning", "learning_status.json")


class LearningAI:

    def __init__(self):
        self.history = self.load_json(HISTORY, [])

    def load_json(self, path, default):
        if not os.path.exists(path):
            return default
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default

    def save_json(self, path, data):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def run(self):
        trades = self.history
        total = len(trades)

        wins = 0
        losses = 0
        total_pnl = 0

        for t in trades:
            pnl = float(t.get("pnl", 0) or 0)
            total_pnl += pnl

            if pnl > 0:
                wins += 1
            elif pnl < 0:
                losses += 1

        win_rate = round((wins / total) * 100, 2) if total else 0

        if total == 0:
            lesson = "NO_TRADE_DATA"
        elif total_pnl > 0:
            lesson = "STRATEGY_POSITIVE"
        elif total_pnl < 0:
            lesson = "STRATEGY_NEGATIVE_REVIEW_REQUIRED"
        else:
            lesson = "STRATEGY_NEUTRAL"

        result = {
            "engine": "learning_ai",
            "status": "READY",
            "mode": "PAPER_ONLY",
            "total_trades": total,
            "wins": wins,
            "losses": losses,
            "win_rate": win_rate,
            "total_pnl": round(total_pnl, 2),
            "lesson": lesson,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.save_json(OUT, result)
        return result


def run():
    return LearningAI().run()


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))