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
    except:
        return default


def save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


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

    def save_all(self):

        self.account["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        save(ACCOUNT, self.account)
        save(POSITIONS, self.positions)
        save(PERFORMANCE, self.performance)

    def get_account(self):
        return self.account

    def get_positions(self):
        return self.positions

    def add_position(self, symbol, side, price, qty):

        self.positions.append({
            "symbol": symbol,
            "side": side,
            "entry": price,
            "qty": qty,
            "opened_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        self.save_all()

    def close_all(self):

        self.positions = []

        self.save_all()


if __name__ == "__main__":

    p = PortfolioEngine()

    p.save_all()

    print("PORTFOLIO_ENGINE_READY")