import json
import os
from datetime import datetime

ROOT = r"C:\ARGOS_STOCK"
OUT = os.path.join(ROOT, "data", "stock", "stock_ai_team_status.json")

from news_ai import run as news_run
from disclosure_ai import run as disclosure_run
from earnings_ai import run as earnings_run
from sector_ai import run as sector_run
from money_flow_ai import run as money_flow_run

def main():
    data = {
        "project": "ARGOS_STOCK",
        "mode": "PAPER_ONLY",
        "real_order": False,
        "api_order": False,
        "auto_real_order": False,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "stock_ai_team": {
            "news_ai": news_run(),
            "disclosure_ai": disclosure_run(),
            "earnings_ai": earnings_run(),
            "sector_ai": sector_run(),
            "money_flow_ai": money_flow_run()
        }
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("ARGOS_STOCK_AI_TEAM_OK")
    print("MODE=PAPER_ONLY")
    print("REAL_ORDER=FALSE")
    print("API_ORDER=FALSE")
    print("AUTO_REAL_ORDER=FALSE")
    print("STATUS_FILE=data/stock/stock_ai_team_status.json")

if __name__ == "__main__":
    main()
