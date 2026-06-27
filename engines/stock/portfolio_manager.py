import json
import os
from datetime import datetime

ROOT = r"C:\ARGOS_STOCK"

DATA = os.path.join(ROOT, "data", "portfolio")

ACCOUNT = os.path.join(DATA, "account.json")
PORTFOLIO = os.path.join(DATA, "portfolio.json")
HISTORY = os.path.join(DATA, "history.json")


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def load(path, default):
    if not os.path.exists(path):
        return default

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


class PortfolioManager:

    def account(self):
        return load(
            ACCOUNT,
            {
                "cash":10000000,
                "equity":10000000,
                "today_pnl":0,
                "total_pnl":0,
                "win":0,
                "loss":0,
                "updated_at":now()
            }
        )

    def portfolio(self):
        return load(PORTFOLIO, [])

    def history(self):
        return load(HISTORY, [])

    def save_all(self, account, portfolio, history):
        account["updated_at"] = now()

        save(ACCOUNT, account)
        save(PORTFOLIO, portfolio)
        save(HISTORY, history)

    def has_position(self, symbol):

        for p in self.portfolio():

            if p["symbol"] == symbol and p["status"] == "OPEN":
                return True

        return False

    def buy(self, symbol, price, qty):

        account = self.account()
        portfolio = self.portfolio()
        history = self.history()

        if self.has_position(symbol):
            return {
                "status":"EXISTS"
            }

        portfolio.append({
            "symbol":symbol,
            "side":"BUY",
            "entry_price":price,
            "qty":qty,
            "status":"OPEN",
            "opened_at":now()
        })

        self.save_all(account, portfolio, history)

        return {
            "status":"BUY_OK"
        }

    def sell(self, symbol, exit_price):

        account = self.account()
        portfolio = self.portfolio()
        history = self.history()

        remain=[]

        result="NOT_FOUND"

        for p in portfolio:

            if p["symbol"]!=symbol or p["status"]!="OPEN":
                remain.append(p)
                continue

            pnl=(exit_price-p["entry_price"])*p["qty"]

            account["cash"]+=pnl
            account["equity"]+=pnl
            account["today_pnl"]+=pnl
            account["total_pnl"]+=pnl

            if pnl>=0:
                account["win"]+=1
            else:
                account["loss"]+=1

            history.append({
                "symbol":symbol,
                "side":"BUY",
                "entry":p["entry_price"],
                "exit":exit_price,
                "qty":p["qty"],
                "pnl":pnl,
                "closed_at":now()
            })

            result="SELL_OK"

        self.save_all(account, remain, history)

        return {
            "status":result
        }


if __name__=="__main__":

    pm=PortfolioManager()

    print(pm.buy("005930",70000,10))
    print(pm.sell("005930",71000))