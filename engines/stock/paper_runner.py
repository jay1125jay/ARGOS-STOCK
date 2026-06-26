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

    def heartbeat(self):

        os.makedirs(os.path.dirname(RUNNER_STATUS), exist_ok=True)

        data = {
            "project": "ARGOS_STOCK",
            "engine": "PaperRunner",
            "mode": "PAPER_ONLY",
            "running": True,
            "real_order": False,
            "api_order": False,
            "auto_real_order": False,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        with open(RUNNER_STATUS, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def loop(self):

        self.datahub.save()

        ai = self.chief.decide()

        decision = self.decision.evaluate(ai)

        self.heartbeat()

        print("=" * 60)
        print("ARGOS STOCK PAPER")
        print("AI :", ai["signal"])
        print("FINAL :", decision["signal"])
        print("ACCOUNT :", self.portfolio.account["cash"])
        print("POSITION :", len(self.portfolio.positions))
        print("HISTORY :", len(self.history.get_all()))

    def start(self):

        print("PAPER RUNNER START")

        self.running = True

        while True:

            self.loop()

            time.sleep(3)


if __name__ == "__main__":

    PaperRunner().start()