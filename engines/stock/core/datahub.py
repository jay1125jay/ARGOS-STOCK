import os

from engines.stock.core.safe_json import SafeJSON

ROOT = r"C:\ARGOS_STOCK"


class DataHub:

    PATHS = {
        "kis": "data/stock/kis_cache.json",
        "technical": "data/technical/technical_status.json",
        "news": "data/news/stock_news_ai.json",
        "disclosure": "data/dart/disclosure_ai_status.json",
        "money_flow": "data/money_flow/money_flow_status.json",
        "sector": "data/sector/sector_status.json",
        "market": "data/market_state/market_state_status.json",
        "macro": "data/macro/macro_ai_status.json",
        "us": "data/us/us_ai_status.json",
        "earnings": "data/earnings/earnings_ai_status.json",
        "risk": "data/risk/risk_status.json",
        "decision": "data/decision/final_decision.json",
        "execution": "data/execution/execution_status.json",
        "portfolio_account": "data/portfolio/account.json",
        "portfolio_positions": "data/portfolio/positions.json",
        "history": "data/history/trade_history.json",
        "report": "data/report/report_status.json",
        "runner": "data/runner/runner_status.json",
        "health": "data/system/health_status.json"
    }

    def path(self, key):
        return os.path.join(ROOT, self.PATHS.get(key, ""))

    def load(self, key, default=None):
        if default is None:
            default = {}
        return SafeJSON.load(self.path(key), default)

    def kis(self):
        return self.load("kis")

    def technical(self):
        return self.load("technical")

    def news(self):
        return self.load("news")

    def disclosure(self):
        return self.load("disclosure")

    def money_flow(self):
        return self.load("money_flow")

    def sector(self):
        return self.load("sector")

    def market(self):
        return self.load("market")

    def macro(self):
        return self.load("macro")

    def us(self):
        return self.load("us")

    def earnings(self):
        return self.load("earnings")

    def risk(self):
        return self.load("risk")

    def decision(self):
        return self.load("decision")

    def execution(self):
        return self.load("execution")

    def account(self):
        return self.load("portfolio_account")

    def positions(self):
        return self.load("portfolio_positions", [])

    def history(self):
        return self.load("history", [])

    def report(self):
        return self.load("report")

    def runner(self):
        return self.load("runner")

    def health(self):
        return self.load("health")

    def snapshot(self):
        return {
            "kis": self.kis(),
            "technical": self.technical(),
            "news": self.news(),
            "disclosure": self.disclosure(),
            "money_flow": self.money_flow(),
            "sector": self.sector(),
            "market": self.market(),
            "macro": self.macro(),
            "us": self.us(),
            "earnings": self.earnings(),
            "risk": self.risk(),
            "decision": self.decision(),
            "execution": self.execution(),
            "account": self.account(),
            "positions": self.positions(),
            "history": self.history(),
            "report": self.report(),
            "runner": self.runner(),
            "health": self.health()
        }


if __name__ == "__main__":
    hub = DataHub()
    s = hub.snapshot()

    print("DATAHUB_READY")
    print("HEALTH:", s["health"].get("health", 0))
    print("DECISION:", s["decision"].get("signal", "WAIT"))
    print("EXECUTION:", s["execution"].get("action", "NO_ACTION"))