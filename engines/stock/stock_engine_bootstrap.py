import json
import os
from datetime import datetime

ROOT = r"C:\ARGOS_STOCK"
SETTINGS = os.path.join(ROOT, "config", "stock", "stock_settings.json")
STATUS = os.path.join(ROOT, "data", "stock", "stock_engine_status.json")

def load_settings():
    with open(SETTINGS, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    s = load_settings()
    data = {
        "project": "ARGOS_STOCK",
        "mode": s.get("mode", "PAPER_ONLY"),
        "real_order": False,
        "api_order": False,
        "auto_real_order": False,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "engines": {
            "news_ai": "READY",
            "disclosure_ai": "READY",
            "earnings_ai": "READY",
            "sector_ai": "READY",
            "money_flow_ai": "READY",
            "head_ai": "READY"
        },
        "markets": s.get("markets", []),
        "kr_watchlist": s.get("kr_watchlist", []),
        "us_watchlist": s.get("us_watchlist", [])
    }

    os.makedirs(os.path.dirname(STATUS), exist_ok=True)
    with open(STATUS, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("ARGOS_STOCK_ENGINE_BOOTSTRAP_OK")
    print("MODE=PAPER_ONLY")
    print("REAL_ORDER=FALSE")
    print("API_ORDER=FALSE")
    print("AUTO_REAL_ORDER=FALSE")
    print("STATUS_FILE=data/stock/stock_engine_status.json")

if __name__ == "__main__":
    main()
