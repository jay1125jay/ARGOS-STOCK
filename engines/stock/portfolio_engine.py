import json
import os
from datetime import datetime

ROOT = r"C:\ARGOS_STOCK"

ACCOUNT = os.path.join(ROOT, "data", "portfolio", "account.json")
POSITIONS = os.path.join(ROOT, "data", "portfolio", "positions.json")
PERFORMANCE = os.path.join(ROOT, "data", "portfolio", "performance.json")


def ensure():
    os.makedirs(os.path.dirname(ACCOUNT), exist_ok=True)


def load(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


class PortfolioEngine:

    def __init__(self):
        ensure()

        self.account = load(ACCOUNT, {
            "cash": 10000000,
            "equity": 10000000,
            "today_pnl": 0,
            "total_pnl": 0,
            "win_rate": 0,
            "trade_count": 0,
            "updated_at": ""
        })

        self.positions = load(POSITIONS, [])

        self.performance = load(PERFORMANCE, {
            "today": 0,
            "week": 0,
            "month": 0,
            "total": 0
        })

    def now(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def save_all(self):
        self.account["updated_at"] = self.now()
        save(ACCOUNT, self.account)
        save(POSITIONS, self.positions)
        save(PERFORMANCE, self.performance)

    def get_account(self):
        return self.account

    def get_positions(self):
        return self.positions

    def has_position(self):
        return len(self.positions) > 0

    def add_position(self, symbol, side, price, qty, reason="PAPER_ENTRY"):
        cost = price * qty

        if side == "BUY" and self.account.get("cash", 0) < cost:
            return False

        if side == "BUY":
            self.account["cash"] = round(self.account.get("cash", 0) - cost, 2)

        self.positions.append({
            "symbol": symbol,
            "side": side,
            "entry": price,
            "qty": qty,
            "cost": round(cost, 2),
            "tp": round(price * 1.02, 2),
            "sl": round(price * 0.99, 2),
            "reason": reason,
            "opened_at": self.now()
        })

        self.save_all()
        return True

    def close_position(self, position, exit_price, reason="PAPER_EXIT"):
        side = position.get("side", "BUY")
        entry = float(position.get("entry", 0))
        qty = float(position.get("qty", 0))

        if side == "BUY":
            gross = exit_price * qty
            pnl = (exit_price - entry) * qty
            self.account["cash"] = round(self.account.get("cash", 0) + gross, 2)
        else:
            gross = 0
            pnl = 0

        self.account["total_pnl"] = round(self.account.get("total_pnl", 0) + pnl, 2)
        self.account["today_pnl"] = round(self.account.get("today_pnl", 0) + pnl, 2)
        self.account["trade_count"] = int(self.account.get("trade_count", 0)) + 1

        self.positions = [
            p for p in self.positions
            if not (
                p.get("symbol") == position.get("symbol")
                and p.get("opened_at") == position.get("opened_at")
            )
        ]

        self.save_all()

        return {
            "symbol": position.get("symbol", ""),
            "side": side,
            "entry": entry,
            "exit": exit_price,
            "qty": qty,
            "pnl": round(pnl, 2),
            "reason": reason,
            "closed_at": self.now()
        }

    def close_all(self):
        self.positions = []
        self.save_all()


if __name__ == "__main__":
    p = PortfolioEngine()
    p.save_all()
    print("PORTFOLIO_ENGINE_READY")