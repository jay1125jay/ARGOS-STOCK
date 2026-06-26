import time

from engines.stock.data_hub import DataHub
from engines.stock.chief_ai import ChiefAI
from engines.stock.decision_center import DecisionCenter
from engines.stock.portfolio_engine import PortfolioEngine
from engines.stock.history_engine import HistoryEngine


class PaperRunner:

    def __init__(self):

        self.datahub = DataHub()

        self.chief = ChiefAI()

        self.decision = DecisionCenter()

        self.portfolio = PortfolioEngine()

        self.history = HistoryEngine()

    def loop(self):

        self.datahub.save()

        ai = self.chief.decide()

        decision = self.decision.evaluate(ai)

        print("=" * 60)
        print("ARGOS STOCK PAPER")
        print("AI :", ai["signal"])
        print("FINAL :", decision["signal"])
        print("ACCOUNT :", self.portfolio.account["cash"])
        print("POSITION :", len(self.portfolio.positions))
        print("HISTORY :", len(self.history.get_all()))

    def start(self):

        print("PAPER RUNNER START")

        while True:

            self.loop()

            time.sleep(3)


if __name__ == "__main__":

    PaperRunner().start()