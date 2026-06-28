import json
import os
from datetime import datetime

ROOT = r"C:\ARGOS_STOCK"

KIS_CACHE = os.path.join(ROOT, "data", "stock", "kis_accum_cache.json")
INDICATOR = os.path.join(ROOT, "data", "indicator", "indicator_status.json")
OUT = os.path.join(ROOT, "data", "technical", "technical_status.json")


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


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


def safe_float(value, default=0):
    try:
        return float(value)
    except Exception:
        return default


def build_indicator_map():
    data = load_json(INDICATOR, {})
    items = data.get("items", [])

    result = {}

    for item in items:
        symbol = item.get("symbol", "")
        if symbol:
            result[symbol] = item

    return result


def analyze_quote(q, indicator_map):
    symbol = q.get("symbol", "")
    price = safe_float(q.get("price", 0))
    change_rate = safe_float(q.get("change_rate", 0))
    volume = safe_float(q.get("volume", 0))

    indicator = indicator_map.get(symbol, {})
    indicator_score = safe_float(indicator.get("score", 0))

    score = 0
    reasons = []

    if price <= 0:
        reasons.append("NO_PRICE")
        return {
            "symbol": symbol,
            "signal": "WAIT",
            "score": -999,
            "price": price,
            "change_rate": change_rate,
            "volume": volume,
            "indicator_score": indicator_score,
            "reason": ",".join(reasons)
        }

    reasons.append("PRICE_OK")

    if change_rate >= 3:
        score += 30
        reasons.append("STRONG_MOMENTUM_UP")
    elif change_rate >= 1:
        score += 15
        reasons.append("MOMENTUM_UP")
    elif change_rate <= -5:
        score -= 30
        reasons.append("STRONG_MOMENTUM_DOWN")
    elif change_rate <= -1:
        score -= 15
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

    if indicator_score > 0:
        score += min(indicator_score, 30)
        reasons.append("INDICATOR_POSITIVE")
    elif indicator_score < 0:
        score += max(indicator_score, -30)
        reasons.append("INDICATOR_NEGATIVE")
    else:
        reasons.append("INDICATOR_NEUTRAL")

    if score >= 60:
        signal = "BUY"
    elif score <= -60:
        signal = "SELL"
    else:
        signal = "WAIT"

    return {
        "symbol": symbol,
        "signal": signal,
        "score": round(score, 2),
        "price": price,
        "change_rate": change_rate,
        "volume": volume,
        "indicator_score": indicator_score,
        "ema5": indicator.get("ema5", 0),
        "ema20": indicator.get("ema20", 0),
        "ema60": indicator.get("ema60", 0),
        "rsi14": indicator.get("rsi14", 50),
        "macd": indicator.get("macd", {}),
        "atr14": indicator.get("atr14", 0),
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
            "raw_count": 0,
            "valid_count": 0,
            "top20": [],
            "items": [],
            "reason": "KIS accum cache not found or empty.",
            "updated_at": now()
        }

        save_json(result)
        return result

    indicator_map = build_indicator_map()

    valid_quotes = []

    for q in quotes:
        if q.get("status") == "QUOTE_OK" and safe_float(q.get("price", 0)) > 0:
            valid_quotes.append(q)

    items = []

    for q in valid_quotes:
        items.append(analyze_quote(q, indicator_map))

    ranked = sorted(
        items,
        key=lambda x: x.get("score", 0),
        reverse=True
    )

    if not ranked:
        result = {
            "engine": "technical_ai",
            "status": "NO_VALID_QUOTES",
            "mode": "PAPER_ONLY",
            "signal": "WAIT",
            "score": 0,
            "best_symbol": "",
            "best_price": 0,
            "raw_count": len(quotes),
            "valid_count": 0,
            "top20": [],
            "items": [],
            "reason": "No valid QUOTE_OK data.",
            "updated_at": now()
        }

        save_json(result)
        return result

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
        "raw_count": len(quotes),
        "valid_count": len(valid_quotes),
        "indicator_count": len(indicator_map),
        "reason": best.get("reason", ""),
        "top20": top20,
        "items": ranked,
        "updated_at": now()
    }

    save_json(result)
    return result


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))