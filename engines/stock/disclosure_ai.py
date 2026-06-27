import json
import os
from datetime import datetime

ROOT = r"C:\ARGOS_STOCK"

DART_CACHE = os.path.join(ROOT, "data", "dart", "dart_cache.json")
OUT = os.path.join(ROOT, "data", "dart", "disclosure_ai_status.json")


class DisclosureAI:

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
        t = title.lower()

        negative_words = [
            "유상증자",
            "전환사채",
            "신주인수권",
            "불성실",
            "상장폐지",
            "관리종목",
            "감사의견거절",
            "횡령",
            "배임",
            "소송",
            "손상",
            "적자",
            "정정"
        ]

        positive_words = [
            "자사주",
            "배당",
            "무상증자",
            "수주",
            "계약",
            "실적",
            "영업이익",
            "흑자",
            "합병",
            "투자"
        ]

        score = 0
        hits = []

        for word in negative_words:
            if word in title:
                score -= 15
                hits.append("NEG_" + word)

        for word in positive_words:
            if word in title:
                score += 10
                hits.append("POS_" + word)

        return score, hits

    def run(self):
        cache = self.load_json(DART_CACHE, {})
        disclosures = cache.get("disclosures", [])

        items = []
        total_score = 0

        for d in disclosures[:50]:
            title = d.get("report_nm", "")
            corp = d.get("corp_name", "")
            stock_code = d.get("stock_code", "")
            rcept_no = d.get("rcept_no", "")
            rcept_dt = d.get("rcept_dt", "")

            score, hits = self.score_title(title)
            total_score += score

            items.append({
                "corp_name": corp,
                "stock_code": stock_code,
                "title": title,
                "score": score,
                "hits": hits,
                "rcept_no": rcept_no,
                "rcept_dt": rcept_dt
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
            "engine": "disclosure_ai",
            "status": "READY",
            "mode": "PAPER_ONLY",
            "signal": signal,
            "score": round(total_score, 2),
            "risk": risk,
            "summary": "Disclosure AI analyzed DART disclosure titles.",
            "items": items,
            "updated_at": self.now()
        }

        self.save_json(OUT, result)
        return result


def run():
    return DisclosureAI().run()


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))