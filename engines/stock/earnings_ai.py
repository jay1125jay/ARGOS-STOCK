import json
import os
from datetime import datetime

ROOT = r"C:\ARGOS_STOCK"

DART_CACHE = os.path.join(ROOT, "data", "dart", "dart_cache.json")
NEWS_STATUS = os.path.join(ROOT, "data", "news", "stock_news_ai.json")
OUT = os.path.join(ROOT, "data", "earnings", "earnings_ai_status.json")


class EarningsAI:

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

    def score_title(self, title):
        score = 0
        hits = []

        positive = [
            "실적",
            "영업이익",
            "매출",
            "흑자",
            "증가",
            "surge",
            "beat",
            "growth",
            "profit"
        ]

        negative = [
            "적자",
            "감소",
            "손실",
            "하락",
            "miss",
            "loss",
            "weak",
            "downgrade"
        ]

        t = title.lower()

        for word in positive:
            if word.lower() in t:
                score += 10
                hits.append("POS_" + word)

        for word in negative:
            if word.lower() in t:
                score -= 10
                hits.append("NEG_" + word)

        return score, hits

    def run(self):
        dart = self.load_json(DART_CACHE, {})
        news = self.load_json(NEWS_STATUS, {})

        disclosures = dart.get("disclosures", [])
        news_items = news.get("items", [])

        items = []
        total_score = 0

        for d in disclosures[:50]:
            title = d.get("report_nm", "")
            corp = d.get("corp_name", "")
            stock_code = d.get("stock_code", "")

            if "실적" not in title and "영업" not in title and "매출" not in title and "손익" not in title:
                continue

            score, hits = self.score_title(title)
            total_score += score

            items.append({
                "source": "DART",
                "corp_name": corp,
                "stock_code": stock_code,
                "title": title,
                "score": score,
                "hits": hits
            })

        for n in news_items[:50]:
            title = n.get("title", "")
            keyword = n.get("keyword", "")

            if not title:
                continue

            if (
                "earnings" not in title.lower()
                and "profit" not in title.lower()
                and "revenue" not in title.lower()
                and "guidance" not in title.lower()
            ):
                continue

            score, hits = self.score_title(title)
            total_score += score

            items.append({
                "source": "NEWS",
                "keyword": keyword,
                "title": title,
                "score": score,
                "hits": hits
            })

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
            "engine": "earnings_ai",
            "status": "READY",
            "mode": "PAPER_ONLY",
            "signal": signal,
            "score": round(total_score, 2),
            "risk": risk,
            "summary": "Earnings AI analyzed DART and News earnings-related signals.",
            "items": items,
            "updated_at": self.now()
        }

        self.save_json(OUT, result)
        return result


def run():
    return EarningsAI().run()


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))