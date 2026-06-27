import json
import os
from datetime import datetime

ROOT = r"C:\ARGOS_STOCK"

KIS_CACHE = os.path.join(ROOT, "data", "stock", "kis_cache.json")
OUT = os.path.join(ROOT, "data", "sector", "sector_status.json")


SECTOR_MAP = {
    "005930": "SEMICONDUCTOR",
    "000660": "SEMICONDUCTOR",
    "035420": "INTERNET",
    "035720": "INTERNET",
    "051910": "BATTERY_CHEMICAL",
    "006400": "BATTERY_CHEMICAL",
    "207940": "BIO",
    "068270": "BIO"
}


class SectorAI:

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

    def score_change(self, change_rate):
        if change_rate >= 3:
            return 20
        if change_rate >= 1:
            return 10
        if change_rate <= -3:
            return -20
        if change_rate <= -1:
            return -10
        return 0

    def run(self):
        cache = self.load_json(KIS_CACHE, {})
        quotes = cache.get("quotes", [])

        sectors = {}

        for q in quotes:
            if q.get("status") != "QUOTE_OK":
                continue

            symbol = q.get("symbol", "")
            sector = SECTOR_MAP.get(symbol, "UNKNOWN")

            change_rate = self.safe_float(q.get("change_rate", 0))
            score = self.score_change(change_rate)

            if sector not in sectors:
                sectors[sector] = {
                    "sector": sector,
                    "symbols": [],
                    "total_change": 0,
                    "total_score": 0,
                    "count": 0
                }

            sectors[sector]["symbols"].append(symbol)
            sectors[sector]["total_change"] += change_rate
            sectors[sector]["total_score"] += score
            sectors[sector]["count"] += 1

        items = []

        for sector, data in sectors.items():
            count = data["count"] or 1
            avg_change = data["total_change"] / count
            avg_score = data["total_score"] / count

            if avg_score >= 10:
                sector_signal = "STRONG"
            elif avg_score <= -10:
                sector_signal = "WEAK"
            else:
                sector_signal = "NEUTRAL"

            items.append({
                "sector": sector,
                "symbols": data["symbols"],
                "avg_change_rate": round(avg_change, 2),
                "score": round(avg_score, 2),
                "signal": sector_signal
            })

        total_score = sum(x.get("score", 0) for x in items)

        if total_score >= 20:
            signal = "BUY_WATCH"
            risk = "LOW"
        elif total_score <= -20:
            signal = "SELL_WATCH"
            risk = "HIGH"
        else:
            signal = "WAIT"
            risk = "NORMAL"

        result = {
            "engine": "sector_ai",
            "status": "READY",
            "mode": "PAPER_ONLY",
            "signal": signal,
            "score": round(total_score, 2),
            "risk": risk,
            "summary": "Sector AI analyzed sector strength from KIS watchlist.",
            "items": items,
            "updated_at": self.now()
        }

        self.save_json(OUT, result)
        return result


def run():
    return SectorAI().run()


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))