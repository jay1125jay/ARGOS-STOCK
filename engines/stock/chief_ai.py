import os

import json
from datetime import datetime

from engines.stock.ai_team import AITeam

ROOT = r"C:\ARGOS_STOCK"
RANKING = os.path.join(ROOT, "data", "ranking", "ranking_status.json")


class ChiefAI:

    def load_ranking(self):
        if not os.path.exists(RANKING):
            return {}

        with open(RANKING, "r", encoding="utf-8") as f:
            return json.load(f)

    def __init__(self):
        self.team = AITeam()

    def pick_best_symbol(self, data):
        technical = data.get("technical", {})
        items = technical.get("items", [])

        if not items:
            return {
                "symbol": "005930",
                "price": 70000,
                "symbol_score": 0,
                "symbol_reason": "NO_TECHNICAL_ITEMS"
            }

        best = sorted(
            items,
            key=lambda x: x.get("score", 0),
            reverse=True
        )[0]

        return {
            "symbol": best.get("symbol", "005930"),
            "price": best.get("best_price", best.get("price", 70000)),
            "symbol_score": best.get("score", 0),
            "symbol_reason": best.get("reason", "")
        }

    def decide(self):
        data = self.team.run()

        buy = 0
        sell = 0
        wait = 0
        scores = []

        for name, engine in data.items():
            signal = engine.get("signal", "WAIT")
            score = engine.get("score", 0)

            try:
                scores.append(float(score))
            except Exception:
                scores.append(0)

            if signal in ["BUY", "BUY_WATCH"]:
                buy += 1
            elif signal in ["SELL", "SELL_WATCH"]:
                sell += 1
            else:
                wait += 1

        avg_score = round(sum(scores) / len(scores), 2) if scores else 0

        picked = self.pick_best_symbol(data)

        ranking = self.load_ranking()
        rank_best = ranking.get("best", {})

        if rank_best:
            picked = {
                "symbol": rank_best.get("symbol", picked["symbol"]),
                "price": rank_best.get("price", picked["price"]),
                "symbol_score": rank_best.get("score", picked["symbol_score"]),
                "symbol_reason": rank_best.get("reason", picked["symbol_reason"])
            }

        if buy >= 3 and buy > sell:
            final = "BUY"
            reason = "BUY_VOTES_DOMINANT"
        elif sell >= 3 and sell > buy:
            final = "SELL"
            reason = "SELL_VOTES_DOMINANT"
        else:
            final = "WAIT"
            reason = "NO_STRONG_CONSENSUS"

        return {
            "engine": "chief_ai",
            "status": "READY",
            "mode": "PAPER_ONLY",
            "real_order": False,
            "api_order": False,
            "auto_real_order": False,
            "signal": final,
            "score": avg_score,
            "symbol": picked["symbol"],
            "price": picked["price"],
            "symbol_score": picked["symbol_score"],
            "buy_votes": buy,
            "sell_votes": sell,
            "wait_votes": wait,
            "reason": reason,
            "symbol_reason": picked["symbol_reason"],
            "modules": data,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


if __name__ == "__main__":
    ai = ChiefAI()
    r = ai.decide()

    print(json.dumps(r, indent=2, ensure_ascii=False))