import json
import os
from datetime import datetime

ROOT = r"C:\ARGOS_STOCK"

OUT = os.path.join(
    ROOT,
    "data",
    "decision",
    "final_decision.json"
)


class DecisionCenter:

    def safe_float(self, value, default=0):
        try:
            return float(value)
        except Exception:
            return default

    def module_score(self, name, module):
        signal = module.get("signal", "WAIT")
        score = self.safe_float(module.get("score", 0))
        risk = module.get("risk", "UNKNOWN")
        block_trade = module.get("block_trade", False)

        points = 0
        reasons = []

        if signal in ["BUY", "BUY_WATCH"]:
            points += 20
            reasons.append(f"{name}_BUY")
        elif signal in ["SELL", "SELL_WATCH"]:
            points -= 20
            reasons.append(f"{name}_SELL")
        else:
            reasons.append(f"{name}_WAIT")

        if score > 0:
            points += min(score, 20)
            reasons.append(f"{name}_SCORE_POSITIVE")
        elif score < 0:
            points += max(score, -20)
            reasons.append(f"{name}_SCORE_NEGATIVE")

        if risk in ["HIGH", "DANGER", "BLOCK"]:
            points -= 30
            reasons.append(f"{name}_RISK_HIGH")

        if block_trade:
            points -= 100
            reasons.append(f"{name}_BLOCK_TRADE")

        return points, reasons

    def evaluate(self, ai=None):
        modules = ai.get("modules", {}) if ai else {}

        total_score = 0
        reasons = []

        for name, module in modules.items():
            points, rs = self.module_score(name, module)
            total_score += points
            reasons.extend(rs)

        chief_signal = ai.get("signal", "WAIT") if ai else "WAIT"

        if chief_signal == "BUY":
            total_score += 20
            reasons.append("CHIEF_BUY")
        elif chief_signal == "SELL":
            total_score -= 20
            reasons.append("CHIEF_SELL")
        else:
            reasons.append("CHIEF_WAIT")

        if total_score >= 70:
            signal = "BUY"
        elif total_score <= -70:
            signal = "SELL"
        else:
            signal = "WAIT"

        result = {
            "project": "ARGOS_STOCK",
            "engine": "decision_center",
            "mode": "PAPER_ONLY",
            "real_order": False,
            "api_order": False,
            "auto_real_order": False,
            "signal": signal,
            "score": round(total_score, 2),
            "symbol": ai.get("symbol", "") if ai else "",
            "price": ai.get("price", 0) if ai else 0,
            "symbol_score": ai.get("symbol_score", 0) if ai else 0,
            "symbol_reason": ai.get("symbol_reason", "") if ai else "",
            "approved": signal in ["BUY", "SELL"],
            "chief_signal": chief_signal,
            "reason": ",".join(reasons),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        os.makedirs(os.path.dirname(OUT), exist_ok=True)

        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        return result


if __name__ == "__main__":
    dc = DecisionCenter()
    print(json.dumps(dc.evaluate(), indent=2, ensure_ascii=False))