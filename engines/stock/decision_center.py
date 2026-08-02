import json
import os
from datetime import datetime

ROOT = r"C:\ARGOS_STOCK"

OUT = os.path.join(
    ROOT,
    "data",
    "decision",
    "final_decision.json",
)

POSITIONS = os.path.join(
    ROOT,
    "data",
    "portfolio",
    "positions.json",
)


class DecisionCenter:

    def safe_float(self, value, default=0):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def load_positions(self):
        if not os.path.exists(POSITIONS):
            return []

        try:
            with open(
                POSITIONS,
                "r",
                encoding="utf-8-sig",
            ) as file:
                positions = json.load(file)
        except (OSError, json.JSONDecodeError):
            return []

        if not isinstance(positions, list):
            return []

        return positions

    def has_position(self, symbol):
        target = str(symbol or "").strip()

        if not target:
            return False

        for position in self.load_positions():
            if not isinstance(position, dict):
                continue

            position_symbol = str(
                position.get("symbol", "")
                or ""
            ).strip()

            position_status = str(
                position.get("status", "OPEN")
                or "OPEN"
            ).upper()

            qty = self.safe_float(
                position.get("qty", 0),
                0,
            )

            if (
                position_symbol == target
                and position_status == "OPEN"
                and qty > 0
            ):
                return True

        return False

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
        ai = ai if isinstance(ai, dict) else {}
        modules = ai.get("modules", {})

        if not isinstance(modules, dict):
            modules = {}

        total_score = 0
        reasons = []

        for name, module in modules.items():
            if not isinstance(module, dict):
                continue

            points, module_reasons = self.module_score(
                name,
                module,
            )

            total_score += points
            reasons.extend(module_reasons)

        chief_signal = str(
            ai.get("signal", "WAIT")
            or "WAIT"
        ).upper()

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

        symbol = str(
            ai.get("symbol", "")
            or ""
        ).strip()

        price = self.safe_float(
            ai.get("price", 0),
            0,
        )

        # SELL은 반드시 실제 보유 중인 동일 종목만 허용한다.
        # 다른 보유 종목으로 임의 변경하지 않는다.
        if signal == "SELL" and not self.has_position(symbol):
            signal = "WAIT"
            reasons.append("SELL_SYMBOL_NOT_HELD")

        result = {
            "project": "ARGOS_STOCK",
            "engine": "decision_center",
            "mode": "PAPER_ONLY",
            "real_order": False,
            "api_order": False,
            "auto_real_order": False,
            "signal": signal,
            "score": round(total_score, 2),
            "symbol": symbol,
            "price": price,
            "symbol_score": ai.get("symbol_score", 0),
            "symbol_reason": ai.get("symbol_reason", ""),
            "approved": signal in ["BUY", "SELL"],
            "chief_signal": chief_signal,
            "reason": ",".join(reasons),
            "updated_at": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        }

        os.makedirs(
            os.path.dirname(OUT),
            exist_ok=True,
        )

        temp_path = f"{OUT}.tmp"

        with open(
            temp_path,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                result,
                file,
                indent=2,
                ensure_ascii=False,
            )
            file.flush()
            os.fsync(file.fileno())

        os.replace(
            temp_path,
            OUT,
        )

        return result


if __name__ == "__main__":
    decision_center = DecisionCenter()

    print(
        json.dumps(
            decision_center.evaluate(),
            indent=2,
            ensure_ascii=False,
        )
    )