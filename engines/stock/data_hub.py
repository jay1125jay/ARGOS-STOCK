import json
import os
from datetime import datetime

ROOT = r"C:\ARGOS_STOCK"
OUT = os.path.join(ROOT, "data", "stock", "data_hub_status.json")

def section(name, status="READY"):
    return {
        "name": name,
        "status": status,
        "mode": "PAPER_ONLY",
        "source": "PLACEHOLDER",
        "connected": False,
        "last_update": None,
        "note": "Structure ready. API connection will be added later."
    }

def main():
    data = {
        "project": "ARGOS_STOCK",
        "engine": "data_hub",
        "mode": "PAPER_ONLY",
        "real_order": False,
        "api_order": False,
        "auto_real_order": False,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data_sections": {
            "kr_price": section("KR_PRICE"),
            "us_price": section("US_PRICE"),
            "dart_disclosure": section("DART_DISCLOSURE"),
            "sec_filing": section("SEC_FILING"),
            "news": section("NEWS"),
            "earnings": section("EARNINGS"),
            "sector": section("SECTOR"),
            "money_flow": section("MONEY_FLOW"),
            "fx_rate": section("FX_RATE"),
            "macro": section("MACRO"),
            "vix": section("VIX")
        }
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("ARGOS_STOCK_DATA_HUB_OK")
    print("MODE=PAPER_ONLY")
    print("REAL_ORDER=FALSE")
    print("API_ORDER=FALSE")
    print("AUTO_REAL_ORDER=FALSE")
    print("STATUS_FILE=data/stock/data_hub_status.json")

if __name__ == "__main__":
    main()
