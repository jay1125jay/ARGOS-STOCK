import json
import os
import time
from datetime import datetime

ROOT = r"C:\ARGOS_STOCK"

RUNNER_STATUS = os.path.join(ROOT, "data", "runner", "runner_status.json")
DECISION = os.path.join(ROOT, "data", "decision", "final_decision.json")
PORTFOLIO = os.path.join(ROOT, "data", "portfolio", "account.json")
POSITIONS = os.path.join(ROOT, "data", "portfolio", "positions.json")
HISTORY = os.path.join(ROOT, "data", "history", "trade_history.json")


def ensure():
    os.makedirs(os.path.dirname(RUNNER_STATUS), exist_ok=True)
    os.makedirs(os.path.dirname(DECISION), exist_ok=True)
    os.makedirs(os.path.dirname(PORTFOLIO), exist_ok=True)
    os.makedirs(os.path.dirname(HISTORY), exist_ok=True)


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


class PaperRunner:

    def __init__(self):
        ensure()
        self.mode = "PAPER_ONLY"
        self.running = False

    def heartbeat(self):
        status = {
            "project": "ARGOS_STOCK",
            "engine": "PaperRunner",
            "mode": self.mode,
            "running": self.running,
            "real_order": False,
            "api_order": False,
            "auto_real_order": False,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save(RUNNER_STATUS, status)

    def cycle(self):

        decision = load(DECISION, {
            "signal": "WAIT"
        })

        account = load(PORTFOLIO, {})
        positions = load(POSITIONS, [])
        history = load(HISTORY, [])

        print("=" * 60)
        print("ARGOS STOCK PAPER RUNNER")
        print("MODE :", self.mode)
        print("SIGNAL :", decision.get("signal", "WAIT"))
        print("ACCOUNT :", account.get("cash", 0))
        print("POSITIONS :", len(positions))
        print("HISTORY :", len(history))

    def start(self):

        self.running = True

        while self.running:

            self.heartbeat()

            self.cycle()

            time.sleep(3)

    def stop(self):

        self.running = False


if __name__ == "__main__":

    runner = PaperRunner()

    runner.start()