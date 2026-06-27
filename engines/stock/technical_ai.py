import json
import os
from datetime import datetime


ROOT = r"C:\ARGOS_STOCK"
KIS_CACHE = os.path.join(ROOT, "data", "stock", "kis_cache.json")
OUT = os.path.join(ROOT, "data", "technical", "technical_status.json")


def save_json(data):
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_json(path, default):
    if not os.path.exists(path):
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def analyze_quote(q):
    symbol = q.get("symbol", "")
    price = float(q.get("price", 0) or 0)
    change_rate = float(q.get("change_rate", 0) or 0)
    volume = int(float(q.get("volume", 0) or 0))

    score = 0
    reasons = []

    if price <= 0:
        score -= 100
        reasons.append("NO_PRICE")
    else:
        reasons.append("PRICE_OK")

    if change_rate >= 3.0:
        score += 35
        reasons.append("STRONG_MOMENTUM_UP")
    elif change_rate >= 1.0:
        score += 20
        reasons.append("MOMENTUM_UP")
    elif change_rate <= -3.0:
        score -= 35
        reasons.append("STRONG_MOMENTUM_DOWN")
    elif change_rate <= -1.0:
        score -= 20
        reasons.append("MOMENTUM_DOWN")
    else:
        reasons.append("MOMENTUM_FLAT")

    if volume >= 3000000:
        score += 20
        reasons.append("VOLUME_STRONG")
    elif volume >= 1000000:
        score += 10
        reasons.append("VOLUME_OK")
    else:
        score -= 5
        reasons.append("VOLUME_LOW")

    if score >= 35:
        signal = "BUY"
    elif score <= -35:
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
        result = {
            "engine": "technical_ai",
            "status": "NO_KIS_CACHE",
            "mode": "PAPER_ONLY",
            "signal": "WAIT",
            "score": 0,
            "best_symbol": "",
            "best_price": 0,
            "top20": [],
            "reason": "KIS cache not found or empty.",
            "items": [],
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        save_json(result)
        return result

    items = [analyze_quote(q) for q in quotes]

    ranked = sorted(
        items,
        key=lambda x: x.get("score", 0),
        reverse=True
    )

    best = ranked[0]
    top20 = ranked[:20]

    result = {
        "engine": "technical_ai",
        "status": "READY",
        "mode": "PAPER_ONLY",
        "signal": best.get("signal", "WAIT"),
        "score": best.get("score", 0),
        "best_symbol": best.get("symbol", ""),
        "best_price": best.get("price", 0),
        "best_change_rate": best.get("change_rate", 0),
        "best_volume": best.get("volume", 0),
        "reason": best.get("reason", ""),
        "top20": top20,
        "items": items,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    save_json(result)
    return result


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))