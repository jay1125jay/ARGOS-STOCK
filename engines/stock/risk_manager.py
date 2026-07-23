import json
import os
from datetime import datetime

ROOT = r"C:\ARGOS_STOCK"

ACCOUNT = os.path.join(
    ROOT,
    "data",
    "portfolio",
    "account.json",
)

POSITIONS = os.path.join(
    ROOT,
    "data",
    "portfolio",
    "positions.json",
)

RISK_STATUS = os.path.join(
    ROOT,
    "data",
    "risk",
    "risk_status.json",
)

MODE = "PAPER_ONLY"

MAX_POSITIONS = 5
MAX_POSITION_RATIO = 0.20
MAX_DAILY_LOSS_RATIO = 0.03
MAX_DAILY_TRADES = 10
MAX_CONSECUTIVE_LOSSES = 3
MIN_ORDER_AMOUNT = 10000.0


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def load_json(path, default):
    if not os.path.exists(path):
        return default

    try:
        with open(path, "r", encoding="utf-8-sig") as file:
            return json.load(file)
    except Exception:
        return default


def save_json(path, data):
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

    os.replace(temp_path, path)


class RiskManager:

    def __init__(self):
        self.account = load_json(
            ACCOUNT,
            {},
        )

        self.positions = load_json(
            POSITIONS,
            [],
        )

        if not isinstance(self.account, dict):
            self.account = {}

        if not isinstance(self.positions, list):
            self.positions = []

    def result(
        self,
        approved,
        reason,
        signal,
        symbol,
        price,
        qty,
    ):
        result = {
            "engine": "risk_manager",
            "status": "APPROVED" if approved else "BLOCKED",
            "mode": MODE,
            "approved": approved,
            "reason": reason,
            "signal": signal,
            "symbol": symbol,
            "price": price,
            "qty": qty,
            "position_count": len(self.positions),
            "cash": round(
                float(
                    self.account.get("cash", 0)
                    or 0
                ),
                2,
            ),
            "equity": round(
                float(
                    self.account.get("equity", 0)
                    or 0
                ),
                2,
            ),
            "today_pnl": round(
                float(
                    self.account.get("today_pnl", 0)
                    or 0
                ),
                2,
            ),
            "trade_count": int(
                self.account.get("trade_count", 0)
                or 0
            ),
            "updated_at": now(),
        }

        save_json(
            RISK_STATUS,
            result,
        )

        return result

    def has_position(self, symbol):
        return any(
            str(position.get("symbol", ""))
            == str(symbol)
            for position in self.positions
        )

    def get_position(self, symbol):
        for position in self.positions:
            if (
                str(position.get("symbol", ""))
                == str(symbol)
            ):
                return position

        return None

    def evaluate(
        self,
        signal,
        symbol,
        price,
        qty=1,
    ):
        signal = str(
            signal or "WAIT"
        ).upper()

        symbol = str(
            symbol or ""
        )

        try:
            price = float(price or 0)
            qty = float(qty or 0)
        except (TypeError, ValueError):
            return self.result(
                False,
                "INVALID_NUMBER",
                signal,
                symbol,
                0,
                0,
            )

        if MODE != "PAPER_ONLY":
            return self.result(
                False,
                "LIVE_MODE_BLOCKED",
                signal,
                symbol,
                price,
                qty,
            )

        if signal in (
            "WAIT",
            "HOLD",
            "BLOCK",
        ):
            return self.result(
                False,
                "NO_ORDER_SIGNAL",
                signal,
                symbol,
                price,
                qty,
            )

        if signal not in (
            "BUY",
            "SELL",
        ):
            return self.result(
                False,
                "INVALID_SIGNAL",
                signal,
                symbol,
                price,
                qty,
            )

        if not symbol:
            return self.result(
                False,
                "INVALID_SYMBOL",
                signal,
                symbol,
                price,
                qty,
            )

        if price <= 0:
            return self.result(
                False,
                "INVALID_PRICE",
                signal,
                symbol,
                price,
                qty,
            )

        if qty <= 0:
            return self.result(
                False,
                "INVALID_QTY",
                signal,
                symbol,
                price,
                qty,
            )

        if signal == "BUY":
            return self.evaluate_buy(
                symbol,
                price,
                qty,
            )

        return self.evaluate_sell(
            symbol,
            price,
            qty,
        )

    def evaluate_buy(
        self,
        symbol,
        price,
        qty,
    ):
        cash = float(
            self.account.get("cash", 0)
            or 0
        )

        equity = float(
            self.account.get(
                "equity",
                cash,
            )
            or cash
        )

        initial_cash = float(
            self.account.get(
                "initial_cash",
                10000000.0,
            )
            or 10000000.0
        )

        today_pnl = float(
            self.account.get("today_pnl", 0)
            or 0
        )

        trade_count = int(
            self.account.get("trade_count", 0)
            or 0
        )

        consecutive_losses = int(
            self.account.get(
                "consecutive_losses",
                0,
            )
            or 0
        )

        order_amount = round(
            price * qty,
            2,
        )

        max_position_amount = round(
            equity * MAX_POSITION_RATIO,
            2,
        )

        max_daily_loss = round(
            initial_cash
            * MAX_DAILY_LOSS_RATIO,
            2,
        )

        if self.has_position(symbol):
            return self.result(
                False,
                "DUPLICATE_POSITION",
                "BUY",
                symbol,
                price,
                qty,
            )

        if len(self.positions) >= MAX_POSITIONS:
            return self.result(
                False,
                "MAX_POSITIONS",
                "BUY",
                symbol,
                price,
                qty,
            )

        if order_amount < MIN_ORDER_AMOUNT:
            return self.result(
                False,
                "MIN_ORDER_AMOUNT",
                "BUY",
                symbol,
                price,
                qty,
            )

        if order_amount > max_position_amount:
            return self.result(
                False,
                "MAX_POSITION_AMOUNT",
                "BUY",
                symbol,
                price,
                qty,
            )

        if cash < order_amount:
            return self.result(
                False,
                "INSUFFICIENT_CASH",
                "BUY",
                symbol,
                price,
                qty,
            )

        if today_pnl <= -max_daily_loss:
            return self.result(
                False,
                "DAILY_LOSS_LIMIT",
                "BUY",
                symbol,
                price,
                qty,
            )

        if trade_count >= MAX_DAILY_TRADES:
            return self.result(
                False,
                "DAILY_TRADE_LIMIT",
                "BUY",
                symbol,
                price,
                qty,
            )

        if (
            consecutive_losses
            >= MAX_CONSECUTIVE_LOSSES
        ):
            return self.result(
                False,
                "CONSECUTIVE_LOSS_LIMIT",
                "BUY",
                symbol,
                price,
                qty,
            )

        return self.result(
            True,
            "APPROVED",
            "BUY",
            symbol,
            price,
            qty,
        )

    def evaluate_sell(
        self,
        symbol,
        price,
        qty,
    ):
        position = self.get_position(symbol)

        if position is None:
            return self.result(
                False,
                "POSITION_NOT_FOUND",
                "SELL",
                symbol,
                price,
                qty,
            )

        position_qty = float(
            position.get("qty", 0)
            or 0
        )

        if qty > position_qty:
            return self.result(
                False,
                "SELL_QTY_EXCEEDED",
                "SELL",
                symbol,
                price,
                qty,
            )

        return self.result(
            True,
            "APPROVED",
            "SELL",
            symbol,
            price,
            qty,
        )


def run(
    signal="WAIT",
    symbol="",
    price=0,
    qty=1,
):
    return RiskManager().evaluate(
        signal=signal,
        symbol=symbol,
        price=price,
        qty=qty,
    )


if __name__ == "__main__":
    print(
        json.dumps(
            run(),
            indent=2,
            ensure_ascii=False,
        )
    )