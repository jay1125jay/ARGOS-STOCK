import json
import os
from datetime import datetime

import requests

ROOT = r"C:\ARGOS_STOCK"

SECRET = os.path.join(ROOT, "config", "kis_secret.json")
STOCK_SETTINGS = os.path.join(ROOT, "config", "stock", "stock_settings.json")
OUT = os.path.join(ROOT, "data", "news", "stock_news_ai.json")


class NewsAI:

    def __init__(self):
        self.secret = self.load_json(SECRET, {})
        self.settings = self.load_json(STOCK_SETTINGS, {})

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

    def api_key(self):
        return self.secret.get("news_api_key", "")

    def keywords(self):
        return [
            "Samsung Electronics",
            "SK Hynix",
            "Naver",
            "Kakao",
            "LG Chem",
            "Samsung SDI",
            "Samsung Biologics",
            "Celltrion",
            "Korea stock market",
            "KOSPI"
        ]

    def analyze_text(self, text):
        t = text.lower()

        positive_words = [
            "surge", "beat", "growth", "profit", "upgrade",
            "record", "strong", "rally", "positive", "approval"
        ]

        negative_words = [
            "fall", "drop", "loss", "downgrade", "risk",
            "probe", "lawsuit", "weak", "concern", "negative"
        ]

        score = 0
        hits = []

        for word in positive_words:
            if word in t:
                score += 5
                hits.append("POS_" + word.upper())

        for word in negative_words:
            if word in t:
                score -= 5
                hits.append("NEG_" + word.upper())

        return score, hits

    def mock_news(self):
        items = []

        for keyword in self.keywords():
            items.append({
                "keyword": keyword,
                "title": "MOCK NEWS - waiting for NewsAPI key",
                "source": "MOCK",
                "url": "",
                "score": 0,
                "hits": [],
                "published_at": ""
            })

        return items

    def fetch_newsapi(self):
        key = self.api_key()

        if not key:
            return self.mock_news(), "MOCK_READY"

        items = []

        for keyword in self.keywords():
            try:
                res = requests.get(
                    "https://newsapi.org/v2/everything",
                    params={
                        "q": keyword,
                        "language": "en",
                        "sortBy": "publishedAt",
                        "pageSize": 3,
                        "apiKey": key
                    },
                    timeout=10
                )

                if res.status_code != 200:
                    items.append({
                        "keyword": keyword,
                        "title": "NEWSAPI_FAIL",
                        "source": "NewsAPI",
                        "url": "",
                        "score": 0,
                        "hits": ["NEWSAPI_FAIL"],
                        "published_at": "",
                        "message": res.text
                    })
                    continue

                data = res.json()
                articles = data.get("articles", [])

                for article in articles:
                    title = article.get("title", "") or ""
                    desc = article.get("description", "") or ""
                    text = title + " " + desc

                    score, hits = self.analyze_text(text)

                    items.append({
                        "keyword": keyword,
                        "title": title,
                        "source": article.get("source", {}).get("name", "NewsAPI"),
                        "url": article.get("url", ""),
                        "score": score,
                        "hits": hits,
                        "published_at": article.get("publishedAt", "")
                    })

            except Exception as e:
                items.append({
                    "keyword": keyword,
                    "title": "NEWSAPI_ERROR",
                    "source": "NewsAPI",
                    "url": "",
                    "score": 0,
                    "hits": ["NEWSAPI_ERROR"],
                    "published_at": "",
                    "message": str(e)
                })

        return items, "REAL_READY"

    def run(self):
        items, status = self.fetch_newsapi()

        total_score = sum(float(x.get("score", 0) or 0) for x in items)

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
            "engine": "news_ai",
            "status": status,
            "mode": "PAPER_ONLY",
            "signal": signal,
            "score": round(total_score, 2),
            "risk": risk,
            "summary": "News AI analyzed stock-related headlines.",
            "items": items,
            "updated_at": self.now()
        }

        self.save_json(OUT, result)
        return result


def run():
    return NewsAI().run()


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))