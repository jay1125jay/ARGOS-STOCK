import time

from engines.stock.data_hub import DataHub
from engines.stock.chief_ai import ChiefAI
from engines.stock.portfolio_engine import PortfolioEngine
from engines.stock.decision_center import DecisionCenter
from engines.stock.history_engine import HistoryEngine
from engines.stock.paper_runner import PaperRunner


class RunMode:

    def __init__(self):

        self.data_hub = DataHub()

        self.chief_ai = ChiefAI()

        self.portfolio = PortfolioEngine()

        self.decision = DecisionCenter()

        self.history = HistoryEngine()

        self.runner = PaperRunner()

    def cycle(self):

        self.data_hub.save()

        ai_result = self.chief_ai.decide()

        print("=" * 60)
        print("ARGOS STOCK")
        print("MODE : PAPER_ONLY")
        print("AI SIGNAL :", ai_result["signal"])
        print("ACCOUNT :", self.portfolio.account["cash"])
        print("POSITIONS :", len(self.portfolio.positions))
        print("TRADES :", len(self.history.get_all()))

        self.runner.heartbeat()

    def start(self):

        print("RUN MODE STARTED")

        while True:

            self.cycle()

            time.sleep(3)


if __name__ == "__main__":

    RunMode().start()