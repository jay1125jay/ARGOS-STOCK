import json
import os
from datetime import datetime

ROOT = r"C:\ARGOS_STOCK"

PORTFOLIO = os.path.join(ROOT, "data", "portfolio", "portfolio.json")


def load():
    if not os.path.exists(PORTFOLIO):
        return []

    with open(PORTFOLIO, "r", encoding="utf-8") as f:
        return json.load(f)


def save(data):
    with open(PORTFOLIO, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


class PositionManager:

    TP = 0.03
    SL = -0.02
    TRAIL = 0.015

    def check(self, prices):

        portfolio = load()

        actions = []

        changed = False

        for p in portfolio:

            if p["status"] != "OPEN":
                continue

            symbol = p["symbol"]

            if symbol not in prices:
                continue

            current = prices[symbol]

            entry = p["entry_price"]

            pnl = (current - entry) / entry

            p["current_price"] = current
            p["profit_rate"] = round(pnl * 100, 2)
            p["checked_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            highest = p.get("highest_price", entry)

            if current > highest:
                highest = current

            p["highest_price"] = highest

            if pnl >= self.TP:

                actions.append({
                    "symbol": symbol,
                    "action": "TAKE_PROFIT"
                })

            elif pnl <= self.SL:

                actions.append({
                    "symbol": symbol,
                    "action": "STOP_LOSS"
                })

            elif highest > entry:

                drawdown = (highest - current) / highest

                if drawdown >= self.TRAIL:

                    actions.append({
                        "symbol": symbol,
                        "action": "TRAIL_STOP"
                    })

            changed = True

        if changed:
            save(portfolio)

        return {
            "engine": "position_manager",
            "status": "READY",
            "positions": len(portfolio),
            "actions": actions
        }


if __name__ == "__main__":

    prices = {
        "005930": 71500
    }

    print(PositionManager().check(prices))