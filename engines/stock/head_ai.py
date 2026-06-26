import json
import os
from datetime import datetime

ROOT = r"C:\ARGOS_STOCK"
OUT = os.path.join(ROOT, "data", "stock", "head_ai_status.json")

from news_ai import run as news_run
from disclosure_ai import run as disclosure_run
from earnings_ai import run as earnings_run
from sector_ai import run as sector_run
from money_flow_ai import run as money_flow_run

def decide(modules):
    risks = [m.get("risk", "UNKNOWN") for m in modules.values()]
    signals = [m.get("signal", "WAIT") for m in modules.values()]

    if "HIGH" in risks:
        return "WAIT", "HIGH_RISK_BLOCK"
    if signals.count("BUY") >= 3:
        return "BUY_WATCH", "MULTI_ENGINE_BUY_BIAS"
    if signals.count("SELL") >= 3:
        return "SELL_WATCH", "MULTI_ENGINE_SELL_BIAS"
    return "WAIT", "NO_STRONG_CONSENSUS"

def main():
    modules = {
        "news_ai": news_run(),
        "disclosure_ai": disclosure_run(),
        "earnings_ai": earnings_run(),
        "sector_ai": sector_run(),
        "money_flow_ai": money_flow_run()
    }

    final_signal, reason = decide(modules)

    data = {
        "project": "ARGOS_STOCK",
        "mode": "PAPER_ONLY",
        "real_order": False,
        "api_order": False,
        "auto_real_order": False,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "final_signal": final_signal,
        "reason": reason,
        "modules": modules
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("ARGOS_STOCK_HEAD_AI_OK")
    print("FINAL_SIGNAL=" + final_signal)
    print("REASON=" + reason)
    print("MODE=PAPER_ONLY")
    print("REAL_ORDER=FALSE")
    print("API_ORDER=FALSE")
    print("AUTO_REAL_ORDER=FALSE")

if __name__ == "__main__":
    main()
