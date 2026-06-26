import json
import os
from datetime import datetime

ROOT = r"C:\ARGOS_STOCK"

HEAD_AI = os.path.join(ROOT, "data", "stock", "head_ai_status.json")
DECISION = os.path.join(ROOT, "data", "decision", "final_decision.json")


def ensure():
    os.makedirs(os.path.dirname(DECISION), exist_ok=True)


def load(path, default):
    if not os.path.exists(path):
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default


def save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


class DecisionCenter:

    def __init__(self):
        ensure()

    def evaluate(self):

        head = load(HEAD_AI, {})

        signal = head.get("final_signal", "WAIT")

        if signal not in [
            "BUY",
            "SELL",
            "BUY_WATCH",
            "SELL_WATCH",
            "WAIT",
            "BLOCK"
        ]:
            signal = "WAIT"

        result = {
            "project": "ARGOS_STOCK",
            "mode": "PAPER_ONLY",
            "real_order": False,
            "api_order": False,
            "auto_real_order": False,
            "signal": signal,
            "approved": signal not in ["WAIT", "BLOCK"],
            "reason": head.get("reason", ""),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        save(DECISION, result)

        return result


if __name__ == "__main__":

    dc = DecisionCenter()

    r = dc.evaluate()

    print("=" * 60)
    print("DECISION CENTER")
    print("SIGNAL :", r["signal"])
    print("APPROVED :", r["approved"])
    print("MODE :", r["mode"])