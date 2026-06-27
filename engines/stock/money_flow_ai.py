import json
import os
from datetime import datetime

ROOT = r"C:\ARGOS_STOCK"

KIS_CACHE = os.path.join(ROOT, "data", "stock", "kis_cache.json")
OUT = os.path.join(ROOT, "data", "money_flow", "money_flow_status.json")


class MoneyFlowAI:

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

    def score_quote(self, quote):
        raw = quote.get("raw", {})

        foreign_net = self.safe_float(raw.get("frgn_ntby_qty", 0))
        program_net = self.safe_float(raw.get("pgtr_ntby_qty", 0))
        foreign_rate = self.safe_float(raw.get("hts_frgn_ehrt", 0))

        score = 0
        hits = []

        if foreign_net > 0:
            score += 10
            hits.append("FOREIGN_BUY")
        elif foreign_net < 0:
            score -= 10
            hits.append("FOREIGN_SELL")

        if program_net > 0:
            score += 5
            hits.append("PROGRAM_BUY")
        elif program_net < 0:
            score -= 5
            hits.append("PROGRAM_SELL")

        if foreign_rate >= 40:
            score += 5
            hits.append("FOREIGN_HOLDING_HIGH")
        elif foreign_rate <= 10 and foreign_rate > 0:
            score -= 5
            hits.append("FOREIGN_HOLDING_LOW")

        return {
            "symbol": quote.get("symbol", ""),
            "price": quote.get("price", 0),
            "foreign_net_qty": foreign_net,
            "program_net_qty": program_net,
            "foreign_holding_rate": foreign_rate,
            "score": score,
            "hits": hits
        }

    def run(self):
        cache = self.load_json(KIS_CACHE, {})
        quotes = cache.get("quotes", [])

        items = []

        for q in quotes:
            if q.get("status") == "QUOTE_OK":
                items.append(self.score_quote(q))

        total_score = sum(x.get("score", 0) for x in items)

        if total_score >= 30:
            signal = "BUY_WATCH"
            risk = "LOW"
        elif total_score <= -30:
            signal = "SELL_WATCH"
            risk = "HIGH"
        else:
            signal = "WAIT"
            risk = "NORMAL"

        result = {
            "engine": "money_flow_ai",
            "status": "READY",
            "mode": "PAPER_ONLY",
            "signal": signal,
            "score": round(total_score, 2),
            "risk": risk,
            "summary": "Money Flow AI analyzed KIS foreign/program flow fields.",
            "items": items,
            "updated_at": self.now()
        }

        self.save_json(OUT, result)
        return result


def run():
    return MoneyFlowAI().run()


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))