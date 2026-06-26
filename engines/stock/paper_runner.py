import json
import os
import time
from datetime import datetime

from engines.stock.data_hub import DataHub
from engines.stock.chief_ai import ChiefAI
from engines.stock.decision_center import DecisionCenter
from engines.stock.portfolio_engine import PortfolioEngine
from engines.stock.history_engine import HistoryEngine

ROOT = r"C:\ARGOS_STOCK"
RUNNER_STATUS = os.path.join(ROOT, "data", "runner", "runner_status.json")


class PaperRunner:

    def __init__(self):
        self.datahub = DataHub()
        self.chief = ChiefAI()
        self.decision = DecisionCenter()
        self.portfolio = PortfolioEngine()
        self.history = HistoryEngine()
        self.running = False

    def heartbeat(self, ai, decision):
        os.makedirs(os.path.dirname(RUNNER_STATUS), exist_ok=True)

        data = {
            "project": "ARGOS_STOCK",
            "engine": "PaperRunner",
            "mode": "PAPER_ONLY",
            "running": self.running,
            "real_order": False,
            "api_order": False,
            "auto_real_order": False,
            "ai_signal": ai.get("signal", "WAIT"),
            "final_signal": decision.get("signal", "WAIT"),
            "account": self.portfolio.account.get("cash", 0),
            "positions": len(self.portfolio.positions),
            "history": len(self.history.get_all()),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        with open(RUNNER_STATUS, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        return data

    def loop(self):
        self.datahub.save()

        ai = self.chief.decide()
        decision = self.decision.evaluate(ai)

        status = self.heartbeat(ai, decision)

        print("=" * 60)
        print("ARGOS STOCK PAPER")
        print("MODE : PAPER_ONLY")
        print("REAL_ORDER : FALSE")
        print("API_ORDER : FALSE")
        print("AUTO_REAL_ORDER : FALSE")
        print("-" * 60)
        print("AI :", ai.get("signal", "WAIT"))
        print("FINAL :", decision.get("signal", "WAIT"))
        print("ACCOUNT :", self.portfolio.account.get("cash", 0))
        print("POSITION :", len(self.portfolio.positions))
        print("HISTORY :", len(self.history.get_all()))

        return status

    def once(self):
        self.running = False
        return self.loop()

    def start(self):
        print("PAPER RUNNER START")
        self.running = True

        while True:
            self.loop()
            time.sleep(3)


if __name__ == "__main__":
    result = PaperRunner().once()
    print(json.dumps(result, indent=2, ensure_ascii=False))