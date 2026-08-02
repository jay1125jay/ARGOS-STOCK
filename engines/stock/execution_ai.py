import hashlib
import json
import os
from datetime import datetime

from engines.stock.order_manager import OrderManager
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

        except (OSError, json.JSONDecodeError):
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

            file.flush()
            os.fsync(file.fileno())

        os.replace(
            temp_path,
            path,
        )

    def build_client_order_key(
        self,
        decision,
        signal,
        symbol,
        price,
        qty,
    ):
        identity_fields = (
            "decision_id",
            "signal_id",
            "updated_at",
            "created_at",
            "generated_at",
        )

        for field in identity_fields:
            value = str(
                decision.get(
                    field,
                    "",
                )
                or ""
            ).strip()

            if value:
                source = {
                    "identity": value,
                    "signal": signal,
                    "symbol": symbol,
                    "price": price,
                    "qty": qty,
                }

                encoded = json.dumps(
                    source,
                    sort_keys=True,
                    ensure_ascii=False,
                ).encode("utf-8")

                digest = hashlib.sha256(
                    encoded
                ).hexdigest()[:24]

                return f"DECISION-{digest}"

        source = {
            "signal": signal,
            "score": decision.get(
                "score",
                0,
            ),
            "symbol": symbol,
            "price": price,
            "qty": qty,
            "reason": decision.get(
                "reason",
                "",
            ),
            "strategy": decision.get(
                "strategy",
                "",
            ),
        }

        encoded = json.dumps(
            source,
            sort_keys=True,
            ensure_ascii=False,
        ).encode("utf-8")

        digest = hashlib.sha256(
            encoded
        ).hexdigest()[:24]

        return f"DECISION-{digest}"

    def find_order_by_client_key(
        self,
        order_manager,
        client_order_key,
    ):
        for order in order_manager.list_orders():
            if (
                str(
                    order.get(
                        "client_order_key",
                        "",
                    )
                )
                == client_order_key
            ):
                return order

        return None

    def build_result(
        self,
        status,
        signal,
        score,
        action,
        symbol,
        price,
        qty,
        portfolio,
        risk_result,
        order_result,
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
            "qty": qty,
            "positions": len(
                portfolio.positions
            ),
            "risk": risk_result,
            "order": order_result,
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
        order_manager = OrderManager()

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
        ).strip()

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

        closed_trade = None
        risk_result = None
        order_result = None

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
                qty=qty,
                portfolio=portfolio,
                risk_result=None,
                order_result=None,
                closed_trade=None,
                history_summary=history_summary,
                reason="NO_ORDER_SIGNAL",
            )

        if not qty.is_integer() or qty <= 0:
            return self.build_result(
                status="BLOCKED",
                signal=signal,
                score=score,
                action="INVALID_ORDER",
                symbol=symbol,
                price=price,
                qty=qty,
                portfolio=portfolio,
                risk_result=None,
                order_result=None,
                closed_trade=None,
                history_summary=history_summary,
                reason="INVALID_INTEGER_QTY",
            )

        execution_qty = int(qty)

        risk_result = RiskManager().evaluate(
            signal=signal,
            symbol=symbol,
            price=price,
            qty=execution_qty,
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
                qty=execution_qty,
                portfolio=portfolio,
                risk_result=risk_result,
                order_result=None,
                closed_trade=None,
                history_summary=history_summary,
                reason=risk_result.get(
                    "reason",
                    "RISK_BLOCKED",
                ),
            )

        matching_position = None

        if signal == "SELL":
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
                    qty=execution_qty,
                    portfolio=portfolio,
                    risk_result=risk_result,
                    order_result=None,
                    closed_trade=None,
                    history_summary=history_summary,
                    reason="POSITION_NOT_FOUND_AFTER_RISK",
                )

            try:
                position_qty = float(
                    matching_position.get(
                        "qty",
                        0,
                    )
                    or 0
                )
            except (TypeError, ValueError):
                position_qty = 0.0

            if (
                not position_qty.is_integer()
                or int(position_qty) != execution_qty
            ):
                return self.build_result(
                    status="BLOCKED",
                    signal=signal,
                    score=score,
                    action="SELL_BLOCKED",
                    symbol=symbol,
                    price=price,
                    qty=execution_qty,
                    portfolio=portfolio,
                    risk_result=risk_result,
                    order_result=None,
                    closed_trade=None,
                    history_summary=history_summary,
                    reason="PARTIAL_SELL_NOT_SUPPORTED",
                )

        client_order_key = self.build_client_order_key(
            decision=decision,
            signal=signal,
            symbol=symbol,
            price=price,
            qty=execution_qty,
        )

        existing_order = self.find_order_by_client_key(
            order_manager=order_manager,
            client_order_key=client_order_key,
        )

        if existing_order is not None:
            return self.build_result(
                status="BLOCKED",
                signal=signal,
                score=score,
                action="DUPLICATE_ORDER_BLOCKED",
                symbol=symbol,
                price=price,
                qty=execution_qty,
                portfolio=portfolio,
                risk_result=risk_result,
                order_result=existing_order,
                closed_trade=None,
                history_summary=history_summary,
                reason="DUPLICATE_CLIENT_ORDER_KEY",
            )

        order_reason = (
            "AI_ENTRY"
            if signal == "BUY"
            else "AI_EXIT"
        )

        strategy = str(
            decision.get(
                "strategy",
                "",
            )
            or ""
        ).strip()

        try:
            order_result = order_manager.create_order(
                symbol=symbol,
                side=signal,
                price=price,
                qty=execution_qty,
                reason=order_reason,
                strategy=strategy,
                client_order_key=client_order_key,
            )

            if not isinstance(order_result, dict):
                raise TypeError("create_order() must return dict")

            if not order_result.get("order_id"):
                raise RuntimeError("create_order() returned no order_id")

            order_result = order_manager.accept_order(
                order_result["order_id"]
            )
            
            if not isinstance(order_result, dict):
                raise TypeError("accept_order() must return dict")

            if not order_result.get("order_id"):
                raise RuntimeError("accept_order() returned no order_id")

            order_result = order_manager.fill_order(
                order_id=order_result["order_id"],
                fill_qty=execution_qty,
                fill_price=price,
            )

            if order_result is None:
                raise RuntimeError("fill_order() returned None")

            if not isinstance(order_result, dict):
                raise TypeError("fill_order() must return dict")

            if not order_result.get("status"):
                raise RuntimeError("fill_order() returned no status")

            if order_result.get("status") != "FILLED":
                return self.build_result(
                    status="BLOCK",
                    signal=signal,
                    score=score,
                    ction="ORDER_NOT_FILLED",
                    symbol=symbol,
                    price=price,
                    qty=execution_qty,
                    portfolio=portfolio,
                    risk_result=risk_result,
                    order_result=order_result,
                    reason=f"ORDER_STATUS:{order_result.get('status')}",
                )

        except (ValueError, KeyError, OSError) as error:
            return self.build_result(
                status="ERROR",
                signal=signal,
                score=score,
                action="ORDER_FAILED",
                symbol=symbol,
                price=price,
                qty=execution_qty,
                portfolio=portfolio,
                risk_result=risk_result,
                order_result=order_result,
                closed_trade=None,
                history_summary=history_summary,
                reason=f"ORDER_MANAGER_ERROR:{error}",
            )

        if order_result.get("status") != "FILLED":
            return self.build_result(
                status="PENDING",
                signal=signal,
                score=score,
                action="ORDER_NOT_FILLED",
                symbol=symbol,
                price=price,
                qty=execution_qty,
                portfolio=portfolio,
                risk_result=risk_result,
                order_result=order_result,
                closed_trade=None,
                history_summary=history_summary,
                reason="WAITING_FOR_FILL",
            )

        filled_price = float(
            order_result.get(
                "average_fill_price",
                price,
            )
            or price
        )

        if abs(filled_price - price) / price > 0.30:
            raise ValueError(
                f"Abnormal fill price detected "
                f"(order={price}, fill={filled_price})"
            )

        if price <= 0:
            raise ValueError(f"Invalid order price: {price}")

        if filled_price <= 0:
            raise ValueError(f"Invalid filled price: {filled_price}")

        filled_qty = int(
            order_result.get(
                "filled_qty",
                execution_qty,
            )
            or execution_qty
        )

        if filled_qty > execution_qty:
            raise ValueError(
                f"Filled quantity exceeds requested quantity "
                f"({filled_qty} > {execution_qty})"
            )

        if filled_qty < 0:
            raise ValueError(
                f"Invalid filled quantity: {filled_qty}"
            )

        if filled_price <= 0:
            return self.build_result(
                status="ERROR",
                signal=signal,
                score=score,
                action="INVALID_FILL_RESULT",
                symbol=symbol,
                price=filled_price,
                qty=filled_qty,
                portfolio=portfolio,
                risk_result=risk_result,
                order_result=order_result,
                closed_trade=None,
                history_summary=history_summary,
                reason="INVALID_FILLED_PRICE",
            )

        if filled_qty <= 0:
            return self.build_result(
                status="ERROR",
                signal=signal,
                score=score,
                action="INVALID_FILL_RESULT",
                symbol=symbol,
                price=filled_price,
                qty=filled_qty,
                portfolio=portfolio,
                risk_result=risk_result,
                order_result=order_result,
                closed_trade=None,
                history_summary=history_summary,
                reason="INVALID_FILLED_QTY",
            )

        if signal == "BUY":
            success = portfolio.add_position(
                symbol=symbol,
                side="BUY",
                price=filled_price,
                qty=filled_qty,
                reason="AI_ENTRY",
                strategy=order_result.get(
                    "strategy",
                    "UNSPECIFIED",
                ),
            )

            if not success:
                return self.build_result(
                    status="ERROR",
                    signal=signal,
                    score=score,
                    action="BUY_RECONCILIATION_REQUIRED",
                    symbol=symbol,
                    price=filled_price,
                    qty=filled_qty,
                    portfolio=portfolio,
                    risk_result=risk_result,
                    order_result=order_result,
                    closed_trade=None,
                    history_summary=history_summary,
                    reason="ORDER_FILLED_PORTFOLIO_BUY_FAILED",
                )

            action = "PAPER_BUY"

        else:
            closed_trade = portfolio.close_position(
                position=matching_position,
                exit_price=filled_price,
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
                    action="SELL_RECONCILIATION_REQUIRED",
                    symbol=symbol,
                    price=filled_price,
                    qty=filled_qty,
                    portfolio=portfolio,
                    risk_result=risk_result,
                    order_result=order_result,
                    closed_trade=None,
                    history_summary=history_summary,
                    reason="ORDER_FILLED_PORTFOLIO_SELL_FAILED",
                )

            try:
                trade_history.add_trade(
                    closed_trade
                )
            except Exception as error:
                return self.build_result(
                    status="ERROR",
                    signal=signal,
                    score=score,
                    action="HISTORY_SAVE_FAILED",
                    symbol=symbol,
                    price=filled_price,
                    qty=filled_qty,
                    portfolio=portfolio,
                    risk_result=risk_result,
                    order_result=order_result,
                    closed_trade=closed_trade,
                    history_summary=history_summary,
                    reason=f"TRADE_HISTORY_ERROR:{error}",
                )

            action = "PAPER_SELL"

        history_summary = trade_history.run()

        return self.build_result(
            status="FILLED",
            signal=signal,
            score=score,
            action=action,
            symbol=symbol,
            price=filled_price,
            qty=filled_qty,
            portfolio=portfolio,
            risk_result=risk_result,
            order_result=order_result,
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
