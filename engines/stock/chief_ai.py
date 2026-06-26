import json
from datetime import datetime

from engines.stock.ai_team import AITeam


class ChiefAI:

    def __init__(self):
        self.team = AITeam()

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
            "buy_votes": buy,
            "sell_votes": sell,
            "wait_votes": wait,
            "reason": reason,
            "modules": data,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


if __name__ == "__main__":
    ai = ChiefAI()
    r = ai.decide()

    print(json.dumps(r, indent=2, ensure_ascii=False))