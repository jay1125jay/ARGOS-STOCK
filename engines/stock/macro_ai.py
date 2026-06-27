import json
import os
from datetime import datetime

ROOT = r"C:\ARGOS_STOCK"

MARKET_STATE = os.path.join(ROOT, "data", "market_state", "market_state_status.json")
OUT = os.path.join(ROOT, "data", "macro", "macro_ai_status.json")


class MacroAI:

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
        market = self.load_json(MARKET_STATE, {})

        market_score = float(market.get("score", 0) or 0)
        market_risk = market.get("risk", "UNKNOWN")
        market_regime = market.get("market", "UNKNOWN")

        score = 0
        reasons = []

        if market_regime == "RISK_ON":
            score += 20
            reasons.append("MARKET_RISK_ON")
        elif market_regime == "RISK_OFF":
            score -= 30
            reasons.append("MARKET_RISK_OFF")
        else:
            reasons.append("MARKET_NEUTRAL")

        if market_risk == "HIGH":
            score -= 20
            reasons.append("MARKET_RISK_HIGH")
        elif market_risk == "LOW":
            score += 10
            reasons.append("MARKET_RISK_LOW")

        if market_score <= -30:
            score -= 10
            reasons.append("MARKET_SCORE_NEGATIVE")
        elif market_score >= 30:
            score += 10
            reasons.append("MARKET_SCORE_POSITIVE")

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
            "engine": "macro_ai",
            "status": "READY",
            "mode": "PAPER_ONLY",
            "signal": signal,
            "score": round(score, 2),
            "risk": risk,
            "summary": "Macro AI V1 uses market state as macro risk proxy.",
            "market_regime": market_regime,
            "market_score": market_score,
            "reason": ",".join(reasons),
            "updated_at": self.now()
        }

        self.save_json(OUT, result)
        return result


def run():
    return MacroAI().run()


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))