import json
import os
from datetime import datetime

ROOT = r"C:\ARGOS_STOCK"

OUT = os.path.join(ROOT, "data", "system", "health_status.json")

CHECKS = {
    "Technical": "data/technical/technical_status.json",
    "News": "data/news/stock_news_ai.json",
    "Disclosure": "data/dart/disclosure_ai_status.json",
    "MoneyFlow": "data/money_flow/money_flow_status.json",
    "Sector": "data/sector/sector_status.json",
    "Market": "data/market_state/market_state_status.json",
    "Macro": "data/macro/macro_ai_status.json",
    "US": "data/us/us_ai_status.json",
    "Earnings": "data/earnings/earnings_ai_status.json",
    "Risk": "data/risk/risk_status.json",
    "Execution": "data/execution/execution_status.json",
    "Report": "data/report/report_status.json"
}


class HealthCheck:

    def now(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def run(self):

        os.makedirs(os.path.dirname(OUT), exist_ok=True)

        items = []
        ok = 0

        for name, rel in CHECKS.items():

            path = os.path.join(ROOT, rel)

            if os.path.exists(path):

                state = "READY"
                ok += 1

            else:

                state = "MISSING"

            items.append({
                "module": name,
                "status": state,
                "path": rel
            })

        result = {
            "engine": "health_check",
            "status": "READY",
            "ok": ok,
            "total": len(items),
            "health": round(ok / len(items) * 100, 1),
            "items": items,
            "updated_at": self.now()
        }

        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

        return result


def run():
    return HealthCheck().run()


if __name__ == "__main__":

    print(json.dumps(run(), indent=2))