import json
import os
import time
from datetime import datetime

from engines.stock.providers.adapters.kis_adapter import KISAdapter
from engines.stock.technical_ai import run as run_technical
from engines.stock.news_ai import run as run_news
from engines.stock.disclosure_ai import run as run_disclosure
from engines.stock.money_flow_ai import run as run_money_flow
from engines.stock.sector_ai import run as run_sector
from engines.stock.market_state_ai import run as run_market
from engines.stock.macro_ai import run as run_macro
from engines.stock.us_ai import run as run_us
from engines.stock.earnings_ai import run as run_earnings
from engines.stock.risk_ai import run as run_risk
from engines.stock.chief_ai import ChiefAI
from engines.stock.decision_center import DecisionCenter
from engines.stock.execution_ai import ExecutionAI
from engines.stock.report_ai import ReportAI
from engines.stock.learning_ai import run as run_learning
from engines.stock.core.process_lock import ProcessLock
from engines.stock.core.safe_json import SafeJSON
from engines.stock.portfolio_manager import PortfolioManager
from engines.stock.position_manager import PositionManager
from engines.stock.pnl_engine import PnLEngine
from engines.stock.history_engine import HistoryEngine
from engines.stock.learning_engine import LearningEngine

ROOT = r"C:\ARGOS_STOCK"

STATUS = os.path.join(ROOT, "data", "runner", "auto_runner_status.json")
STOP_FILE = os.path.join(ROOT, "data", "runner", "auto_runner_stop.flag")

SLEEP_SECONDS = 5


class AutoRunner:

    def now(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def save_status(self, data):
        SafeJSON.save(STATUS, data)

    def should_stop(self):
        return os.path.exists(STOP_FILE)

    def clear_stop(self):
        if os.path.exists(STOP_FILE):
            os.remove(STOP_FILE)

    def request_stop(self):
        os.makedirs(os.path.dirname(STOP_FILE), exist_ok=True)
        with open(STOP_FILE, "w", encoding="utf-8") as f:
            f.write("STOP")

    def run_once(self, loop_count=1):
        steps = []

        def step(name, fn):
            try:
                result = fn()
                steps.append({
                    "step": name,
                    "status": result.get("status", "DONE") if isinstance(result, dict) else "DONE"
                })
                return result
            except Exception as e:
                steps.append({
                    "step": name,
                    "status": "ERROR",
                    "error": str(e)
                })
                return {}

        step("KIS", lambda: KISAdapter().connect())
        technical = step("TECHNICAL", run_technical)
        news = step("NEWS", run_news)
        disclosure = step("DISCLOSURE", run_disclosure)
        money_flow = step("MONEY_FLOW", run_money_flow)
        sector = step("SECTOR", run_sector)
        market = step("MARKET", run_market)
        macro = step("MACRO", run_macro)
        us = step("US", run_us)
        earnings = step("EARNINGS", run_earnings)
        risk = step("RISK", run_risk)

        chief = step("CHIEF", lambda: ChiefAI().decide())
        decision = step("DECISION", lambda: DecisionCenter().evaluate(chief))
        execution = step("EXECUTION", lambda: ExecutionAI().run())
        symbol = decision.get("symbol", "005930")
        price = decision.get("price", 70000)
        signal = decision.get("signal", "WAIT")

        pm = PortfolioManager()

        if signal == "BUY":
            pm.buy(symbol, price, 10)

        elif signal == "SELL":
            pm.sell(symbol, price)

        position = PositionManager().check({
            symbol: price
        })
        pnl = PnLEngine().run()
        history = HistoryEngine().run()

        learning_engine = LearningEngine().run()

        report = step("REPORT", lambda: ReportAI().run())
        learning = step("LEARNING", run_learning)
        
        status = {
            "project": "ARGOS_STOCK",
            "engine": "auto_runner",
            "mode": "PAPER_ONLY",
            "running": True,
            "loop_count": loop_count,
            "final_signal": decision.get("signal", "WAIT"),
            "symbol": symbol,
            "price": price,
            "decision_score": decision.get("score", 0),
            "execution_action": execution.get("action", "NO_ACTION"),
            "positions": position.get("positions", 0),
            "history": history.get("total_trades", 0),
            "portfolio": position,
            "pnl": pnl,
            "history_engine": history,
            "learning": learning_engine,
            "report_signal": report.get("final_signal", "WAIT"),
            "report_score": report.get("total_score", 0),
            "steps": steps,
            "updated_at": self.now()
        }

        self.save_status(status)

        print("=" * 60)
        print("ARGOS STOCK AUTO RUNNER")
        print("MODE : PAPER_ONLY")
        print("-" * 60)
        print("LOOP :", loop_count)
        print("FINAL :", status["final_signal"])
        print("ACTION :", status["execution_action"])
        print("REPORT :", status["report_signal"], status["report_score"])
        print("POSITION :", status["positions"])
        print("HISTORY :", status["history"])
        print("WINRATE :", pnl["win_rate"])
        print("TOTAL PNL :", pnl["total_pnl"])

        return status

    def start(self):
        lock = ProcessLock()

        if not lock.acquire():
            print("AUTO_RUNNER_ALREADY_RUNNING")
            return

        self.clear_stop()

        loop_count = 0

        try:
            while True:
                if self.should_stop():
                    break

                loop_count += 1
                self.run_once(loop_count)
                time.sleep(SLEEP_SECONDS)

        finally:

            lock.release()

            try:

                status = SafeJSON.load(STATUS, {})

                status["running"] = False
                status["stopped_at"] = self.now()

                self.save_status(status)

            except Exception:

                self.save_status({
                    "project": "ARGOS_STOCK",
                    "engine": "auto_runner",
                    "mode": "PAPER_ONLY",
                    "running": False,
                    "stopped_at": self.now()
                })

            print("AUTO_RUNNER_STOPPED")


def start():
    AutoRunner().start()


def stop():
    AutoRunner().request_stop()
    print("AUTO_RUNNER_STOP_REQUESTED")


if __name__ == "__main__":
    start()