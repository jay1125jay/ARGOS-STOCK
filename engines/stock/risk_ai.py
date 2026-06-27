import json
import os
from datetime import datetime

ROOT = r"C:\ARGOS_STOCK"
OUT = os.path.join(ROOT, "data", "risk", "risk_status.json")


def save_json(data):
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def run():
    result = {
        "engine": "risk_ai",
        "status": "READY",
        "mode": "PAPER_ONLY",
        "signal": "WAIT",
        "score": 0,
        "risk": "NORMAL",
        "block_trade": False,
        "real_order": False,
        "api_order": False,
        "auto_real_order": False,
        "reason": "Risk engine ready. No real order allowed.",
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    save_json(result)
    return result


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))