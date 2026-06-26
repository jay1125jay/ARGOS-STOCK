import json
import os
from datetime import datetime


ROOT = r"C:\ARGOS_STOCK"
KIS_CACHE = os.path.join(ROOT, "data", "stock", "kis_cache.json")


def load_json(path, default):
    if not os.path.exists(path):
        return default

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def analyze_quote(q):
    symbol = q.get("symbol", "")
    price = float(q.get("price", 0) or 0)
    change_rate = float(q.get("change_rate", 0) or 0)
    volume = int(q.get("volume", 0) or 0)

    score = 0
    reasons = []

    if price <= 0:
        reasons.append("NO_PRICE")
    else:
        reasons.append("PRICE_OK")

    if change_rate > 1.0:
        score += 20
        reasons.append("MOMENTUM_UP")
    elif change_rate < -1.0:
        score -= 20
        reasons.append("MOMENTUM_DOWN")
    else:
        reasons.append("MOMENTUM_FLAT")

    if volume >= 1000000:
        score += 10
        reasons.append("VOLUME_OK")
    else:
        reasons.append("VOLUME_LOW")

    if score >= 25:
        signal = "BUY"
    elif score <= -25:
        signal = "SELL"
    else:
        signal = "WAIT"

    return {
        "symbol": symbol,
        "signal": signal,
        "score": score,
        "price": price,
        "change_rate": change_rate,
        "volume": volume,
        "reason": ",".join(reasons)
    }


def run():
    cache = load_json(KIS_CACHE, {})

    quotes = cache.get("quotes", [])

    if not quotes:
        return {
            "engine": "technical_ai",
            "status": "NO_KIS_CACHE",
            "mode": "PAPER_ONLY",
            "signal": "WAIT",
            "score": 0,
            "best_symbol": "",
            "reason": "KIS cache not found or empty.",
            "items": [],
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    items = []
    for q in quotes:
        items.append(analyze_quote(q))

    best = sorted(items, key=lambda x: x.get("score", 0), reverse=True)[0]

    return {
        "engine": "technical_ai",
        "status": "READY",
        "mode": "PAPER_ONLY",
        "signal": best.get("signal", "WAIT"),
        "score": best.get("score", 0),
        "best_symbol": best.get("symbol", ""),
        "reason": best.get("reason", ""),
        "items": items,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))