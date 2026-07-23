import json
import os
from datetime import datetime

from engines.stock.portfolio_engine import PortfolioEngine
from engines.stock.risk_manager import RiskManager
from engines.stock.trade_history_engine import TradeHistoryEngine

ROOT = r"C:\ARGOS_STOCK"

DECISION = os.path.join(
    ROOT,
    "data",
    "decision",
    "final_decision.json",
)

OUT = os.path.join(
    ROOT,
    "data",
    "execution",
    "execution_status.json",
)


class ExecutionAI:

    def now(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def load(self, path, default):
        if not os.path.exists(path):
            return default

        try:
            with open(
                path,
                "r",
                encoding="utf-8-sig",
            ) as file:
                return json.load(file)

        except Exception:
            return default

    def save(self, path, data):
        os.makedirs(
            os.path.dirname(path),
            exist_ok=True,
        )

        temp_path = f"{path}.tmp"

        with open(
            temp_path,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                data,
                file,
                indent=2,
                ensure_ascii=False,
            )

        os.replace(
            temp_path,
            path,
        )

    def build_result(
        self,
        status,
        signal,
        score,
        action,
        symbol,
        price,
        portfolio,
        risk_result,
        closed_trade,
        history_summary,
        reason,
    ):
        result = {
            "engine": "execution_ai",
            "status": status,
            "mode": "PAPER_ONLY",
            "signal": signal,
            "score": score,
            "action": action,
            "reason": reason,
            "symbol": symbol,
            "price": price,
            "positions": len(
                portfolio.positions
            ),
            "risk": risk_result,
            "closed_trade": closed_trade,
            "history": history_summary.get(
                "total_trades",
                0,
            ),
            "updated_at": self.now(),
        }

        self.save(
            OUT,
            result,
        )

        return result

    def run(self):
        portfolio = PortfolioEngine()
        trade_history = TradeHistoryEngine()

        decision = self.load(
            DECISION,
            {},
        )

        signal = str(
            decision.get(
                "signal",
                "WAIT",
            )
            or "WAIT"
        ).upper()

        score = decision.get(
            "score",
            0,
        )

        symbol = str(
            decision.get(
                "symbol",
                "",
            )
            or ""
        )

        try:
            price = float(
                decision.get(
                    "price",
                    0,
                )
                or 0
            )
        except (TypeError, ValueError):
            price = 0.0

        try:
            qty = float(
                decision.get(
                    "qty",
                    1,
                )
                or 1
            )
        except (TypeError, ValueError):
            qty = 1.0

        action = "NO_ACTION"
        closed_trade = None
        risk_result = None

        history_summary = trade_history.run()

        if signal not in (
            "BUY",
            "SELL",
        ):
            return self.build_result(
                status="READY",
                signal=signal,
                score=score,
                action="NO_ACTION",
                symbol=symbol,
                price=price,
                portfolio=portfolio,
                risk_result=None,
                closed_trade=None,
                history_summary=history_summary,
                reason="NO_ORDER_SIGNAL",
            )

        risk_result = RiskManager().evaluate(
            signal=signal,
            symbol=symbol,
            price=price,
            qty=qty,
        )

        if not risk_result.get(
            "approved",
            False,
        ):
            return self.build_result(
                status="BLOCKED",
                signal=signal,
                score=score,
                action="RISK_BLOCKED",
                symbol=symbol,
                price=price,
                portfolio=portfolio,
                risk_result=risk_result,
                closed_trade=None,
                history_summary=history_summary,
                reason=risk_result.get(
                    "reason",
                    "RISK_BLOCKED",
                ),
            )

        if signal == "BUY":
            success = portfolio.add_position(
                symbol=symbol,
                side="BUY",
                price=price,
                qty=qty,
                reason="AI_ENTRY",
            )

            if not success:
                return self.build_result(
                    status="ERROR",
                    signal=signal,
                    score=score,
                    action="BUY_FAILED",
                    symbol=symbol,
                    price=price,
                    portfolio=portfolio,
                    risk_result=risk_result,
                    closed_trade=None,
                    history_summary=history_summary,
                    reason="PORTFOLIO_BUY_FAILED",
                )

            action = "PAPER_BUY"

        elif signal == "SELL":
            matching_position = None

            for position in portfolio.positions:
                if (
                    str(
                        position.get(
                            "symbol",
                            "",
                        )
                    )
                    == symbol
                ):
                    matching_position = position
                    break

            if matching_position is None:
                return self.build_result(
                    status="ERROR",
                    signal=signal,
                    score=score,
                    action="SELL_FAILED",
                    symbol=symbol,
                    price=price,
                    portfolio=portfolio,
                    risk_result=risk_result,
                    closed_trade=None,
                    history_summary=history_summary,
                    reason="POSITION_NOT_FOUND_AFTER_RISK",
                )

            closed_trade = portfolio.close_position(
                position=matching_position,
                exit_price=price,
                reason="AI_EXIT",
            )

            if not isinstance(
                closed_trade,
                dict,
            ):
                return self.build_result(
                    status="ERROR",
                    signal=signal,
                    score=score,
                    action="SELL_FAILED",
                    symbol=symbol,
                    price=price,
                    portfolio=portfolio,
                    risk_result=risk_result,
                    closed_trade=None,
                    history_summary=history_summary,
                    reason="PORTFOLIO_SELL_FAILED",
                )

            trade_history.add_trade(
                closed_trade
            )

            action = "PAPER_SELL"

        history_summary = trade_history.run()

        return self.build_result(
            status="READY",
            signal=signal,
            score=score,
            action=action,
            symbol=symbol,
            price=price,
            portfolio=portfolio,
            risk_result=risk_result,
            closed_trade=closed_trade,
            history_summary=history_summary,
            reason="EXECUTED",
        )


def run():
    return ExecutionAI().run()


if __name__ == "__main__":
    print(
        json.dumps(
            run(),
            indent=2,
            ensure_ascii=False,
        )
    )