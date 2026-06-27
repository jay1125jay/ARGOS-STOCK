import json
import os
from datetime import datetime

ROOT = r"C:\ARGOS_STOCK"

KIS_CACHE = os.path.join(ROOT, "data", "stock", "kis_cache.json")
OUT = os.path.join(ROOT, "data", "market_state", "market_state_status.json")


class MarketStateAI:

    def now(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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

    def safe_float(self, value, default=0):
        try:
            return float(value)
        except Exception:
            return default

    def run(self):
        cache = self.load_json(KIS_CACHE, {})
        quotes = cache.get("quotes", [])

        valid = []

        for q in quotes:
            if q.get("status") == "QUOTE_OK":
                valid.append({
                    "symbol": q.get("symbol", ""),
                    "price": self.safe_float(q.get("price", 0)),
                    "change_rate": self.safe_float(q.get("change_rate", 0)),
                    "volume": self.safe_float(q.get("volume", 0))
                })

        count = len(valid)

        if count == 0:
            result = {
                "engine": "market_state_ai",
                "status": "NO_DATA",
                "mode": "PAPER_ONLY",
                "market": "UNKNOWN",
                "signal": "WAIT",
                "score": 0,
                "risk": "UNKNOWN",
                "reason": "No KIS quote data available.",
                "items": [],
                "updated_at": self.now()
            }

            self.save_json(OUT, result)
            return result

        avg_change = sum(x["change_rate"] for x in valid) / count
        rising = len([x for x in valid if x["change_rate"] > 0])
        falling = len([x for x in valid if x["change_rate"] < 0])

        score = 0
        reasons = []

        if avg_change >= 2:
            score += 30
            reasons.append("MARKET_STRONG_UP")
        elif avg_change >= 0.5:
            score += 15
            reasons.append("MARKET_UP")
        elif avg_change <= -2:
            score -= 30
            reasons.append("MARKET_STRONG_DOWN")
        elif avg_change <= -0.5:
            score -= 15
            reasons.append("MARKET_DOWN")
        else:
            reasons.append("MARKET_FLAT")

        if rising >= count * 0.7:
            score += 15
            reasons.append("BREADTH_STRONG")
        elif falling >= count * 0.7:
            score -= 15
            reasons.append("BREADTH_WEAK")
        else:
            reasons.append("BREADTH_MIXED")

        if score >= 30:
            signal = "BUY_WATCH"
            risk = "LOW"
            market = "RISK_ON"
        elif score <= -30:
            signal = "SELL_WATCH"
            risk = "HIGH"
            market = "RISK_OFF"
        else:
            signal = "WAIT"
            risk = "NORMAL"
            market = "NEUTRAL"

        result = {
            "engine": "market_state_ai",
            "status": "READY",
            "mode": "PAPER_ONLY",
            "market": market,
            "signal": signal,
            "score": round(score, 2),
            "risk": risk,
            "avg_change_rate": round(avg_change, 2),
            "rising_count": rising,
            "falling_count": falling,
            "total_count": count,
            "reason": ",".join(reasons),
            "items": valid,
            "updated_at": self.now()
        }

        self.save_json(OUT, result)
        return result


def run():
    return MarketStateAI().run()


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))