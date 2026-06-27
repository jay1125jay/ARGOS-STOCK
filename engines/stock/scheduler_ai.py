import json
import os
from datetime import datetime

from engines.stock.providers.adapters.kis_adapter import KISAdapter
from engines.stock.paper_runner import PaperRunner
from engines.stock.learning_ai import LearningAI

ROOT = r"C:\ARGOS_STOCK"

OUT = os.path.join(ROOT, "data", "scheduler", "scheduler_status.json")


class SchedulerAI:

    def __init__(self):
        self.kis = KISAdapter()
        self.runner = PaperRunner()
        self.learning = LearningAI()

    def now(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def save_json(self, path, data):
        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def run_once(self):
        steps = []

        kis_result = self.kis.connect()
        steps.append({
            "step": "KIS_PROVIDER",
            "status": kis_result.get("status", "UNKNOWN"),
            "connected": kis_result.get("connected", False)
        })

        runner_result = self.runner.once()
        steps.append({
            "step": "PAPER_RUNNER",
            "status": "DONE",
            "final_signal": runner_result.get("final_signal", "WAIT"),
            "decision_score": runner_result.get("decision_score", 0),
            "positions": runner_result.get("positions", 0),
            "history": runner_result.get("history", 0)
        })

        learning_result = self.learning.run()
        steps.append({
            "step": "LEARNING_AI",
            "status": learning_result.get("status", "UNKNOWN"),
            "total_trades": learning_result.get("total_trades", 0),
            "win_rate": learning_result.get("win_rate", 0),
            "lesson": learning_result.get("lesson", "UNKNOWN")
        })

        result = {
            "project": "ARGOS_STOCK",
            "engine": "scheduler_ai",
            "mode": "PAPER_ONLY",
            "real_order": False,
            "api_order": False,
            "auto_real_order": False,
            "status": "READY",
            "steps": steps,
            "updated_at": self.now()
        }

        self.save_json(OUT, result)

        return result


def run():
    return SchedulerAI().run_once()


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))