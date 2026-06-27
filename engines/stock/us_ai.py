import json
import os
from datetime import datetime

from engines.stock.providers.adapters.yahoo_adapter import YahooAdapter
from engines.stock.providers.adapters.sec_adapter import SECAdapter

ROOT = r"C:\ARGOS_STOCK"

NEWS_STATUS = os.path.join(ROOT, "data", "news", "stock_news_ai.json")
MACRO_STATUS = os.path.join(ROOT, "data", "macro", "macro_ai_status.json")
OUT = os.path.join(ROOT, "data", "us", "us_ai_status.json")


class USAI:

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

    def run(self):
        yahoo = YahooAdapter().connect()
        sec = SECAdapter().connect()

        news = self.load_json(NEWS_STATUS, {})
        macro = self.load_json(MACRO_STATUS, {})

        score = 0
        reasons = []

        news_score = float(news.get("score", 0) or 0)
        macro_score = float(macro.get("score", 0) or 0)

        if news_score >= 20:
            score += 15
            reasons.append("US_RELATED_NEWS_POSITIVE")
        elif news_score <= -20:
            score -= 15
            reasons.append("US_RELATED_NEWS_NEGATIVE")
        else:
            reasons.append("US_NEWS_NEUTRAL")

        if macro_score >= 20:
            score += 20
            reasons.append("MACRO_POSITIVE")
        elif macro_score <= -20:
            score -= 25
            reasons.append("MACRO_NEGATIVE")
        else:
            reasons.append("MACRO_NEUTRAL")

        if yahoo.get("connected"):
            reasons.append("YAHOO_CONNECTED")
        else:
            reasons.append("YAHOO_NOT_CONNECTED")

        if sec.get("connected"):
            reasons.append("SEC_CONNECTED")
        else:
            reasons.append("SEC_NOT_CONNECTED")

        if score >= 30:
            signal = "BUY_WATCH"
            risk = "LOW"
        elif score <= -30:
            signal = "SELL_WATCH"
            risk = "HIGH"
        else:
            signal = "WAIT"
            risk = "NORMAL"

        result = {
            "engine": "us_ai",
            "status": "READY",
            "mode": "PAPER_ONLY",
            "signal": signal,
            "score": round(score, 2),
            "risk": risk,
            "summary": "US AI V1 uses Yahoo/SEC connection state plus News/Macro proxy.",
            "yahoo": yahoo,
            "sec": sec,
            "news_score": news_score,
            "macro_score": macro_score,
            "reason": ",".join(reasons),
            "updated_at": self.now()
        }

        self.save_json(OUT, result)
        return result


def run():
    return USAI().run()


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))