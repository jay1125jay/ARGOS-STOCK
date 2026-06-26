import time

from engines.stock.paper_runner import PaperRunner


class RunMode:

    def __init__(self):
        self.runner = PaperRunner()

    def cycle(self):
        return self.runner.loop()

    def start(self):
        print("RUN MODE STARTED")
        print("MODE : PAPER_ONLY")
        print("REAL_ORDER : FALSE")
        print("API_ORDER : FALSE")
        print("AUTO_REAL_ORDER : FALSE")

        while True:
            self.cycle()
            time.sleep(3)


if __name__ == "__main__":
    RunMode().start()