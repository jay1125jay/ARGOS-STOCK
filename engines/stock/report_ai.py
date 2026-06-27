import json
import os
from datetime import datetime

ROOT = r"C:\ARGOS_STOCK"

ENGINES = {
    "technical": "data/technical/technical_status.json",
    "news": "data/news/stock_news_ai.json",
    "disclosure": "data/disclosure/disclosure_status.json",
    "money_flow": "data/money_flow/money_flow_status.json",
    "sector": "data/sector/sector_status.json",
    "market": "data/market_state/market_state_status.json",
    "macro": "data/macro/macro_ai_status.json",
    "us": "data/us/us_ai_status.json",
    "earnings": "data/earnings/earnings_ai_status.json",
    "risk": "data/risk/risk_status.json"
}

OUT_JSON = os.path.join(ROOT, "data", "report", "report_status.json")
OUT_TXT = os.path.join(ROOT, "reports", "argos_report.txt")


class ReportAI:

    def now(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def load(self, rel):
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}

    def run(self):

        os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
        os.makedirs(os.path.dirname(OUT_TXT), exist_ok=True)

        modules = {}
        total_score = 0

        for name, rel in ENGINES.items():

            d = self.load(rel)

            score = float(d.get("score", 0) or 0)

            modules[name] = {
                "signal": d.get("signal", "WAIT"),
                "score": score,
                "risk": d.get("risk", "UNKNOWN")
            }

            total_score += score

        if total_score >= 50:
            final = "BUY"
        elif total_score <= -50:
            final = "SELL"
        else:
            final = "WAIT"

        report = {
            "engine": "report_ai",
            "status": "READY",
            "mode": "PAPER_ONLY",
            "final_signal": final,
            "total_score": round(total_score, 2),
            "modules": modules,
            "updated_at": self.now()
        }

        with open(OUT_JSON, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        with open(OUT_TXT, "w", encoding="utf-8") as f:

            f.write("=" * 60 + "\n")
            f.write("ARGOS STOCK REPORT\n")
            f.write("=" * 60 + "\n\n")

            for k, v in modules.items():
                f.write(
                    f"{k.upper():15}"
                    f"{v['signal']:12}"
                    f"{v['score']:8}\n"
                )

            f.write("\n")
            f.write(f"TOTAL SCORE : {round(total_score,2)}\n")
            f.write(f"FINAL       : {final}\n")

        return report


def run():
    return ReportAI().run()


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))