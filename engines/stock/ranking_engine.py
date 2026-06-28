import json
import os
from datetime import datetime

ROOT = r"C:\ARGOS_STOCK"

TECH = os.path.join(ROOT, "data", "technical", "technical_status.json")
OUT = os.path.join(ROOT, "data", "ranking", "ranking_status.json")


class RankingEngine:

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

    def run(self):
        tech = self.load_json(TECH, {})
        items = tech.get("items", [])

        valid = []

        for item in items:
            price = float(item.get("price", 0) or 0)
            score = float(item.get("score", 0) or 0)

            if price > 0 and score > -900:
                valid.append(item)

        ranking = sorted(
            valid,
            key=lambda x: x.get("score", 0),
            reverse=True
        )

        best = ranking[0] if ranking else {}

        result = {
            "engine": "ranking_engine",
            "status": "READY" if ranking else "NO_VALID_RANKING",
            "mode": "PAPER_ONLY",
            "source": "technical_ai_v2",
            "raw_count": len(items),
            "valid_count": len(valid),
            "best": best,
            "top10": ranking[:10],
            "top20": ranking[:20],
            "updated_at": self.now()
        }

        os.makedirs(os.path.dirname(OUT), exist_ok=True)

        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        return result


def run():
    return RankingEngine().run()


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))