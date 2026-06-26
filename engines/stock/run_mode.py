import time

from engines.stock.paper_runner import PaperRunner
from engines.stock.portfolio_engine import PortfolioEngine
from engines.stock.decision_center import DecisionCenter
from engines.stock.history_engine import HistoryEngine


class RunMode:

    def __init__(self):

        self.runner = PaperRunner()

        self.portfolio = PortfolioEngine()

        self.decision = DecisionCenter()

        self.history = HistoryEngine()

    def cycle(self):

        decision = self.decision.evaluate()

        signal = decision["signal"]

        print("=" * 60)

        print("ARGOS STOCK")

        print("MODE :", "PAPER_ONLY")

        print("SIGNAL :", signal)

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