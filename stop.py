import json
import os
from datetime import datetime

ROOT = r"C:\ARGOS_STOCK"

RUNNER = os.path.join(
    ROOT,
    "data",
    "runner",
    "runner_status.json"
)


def stop():

    os.makedirs(os.path.dirname(RUNNER), exist_ok=True)

    data = {
        "project": "ARGOS_STOCK",
        "mode": "PAPER_ONLY",
        "status": "STOPPED",
        "running": False,
        "real_order": False,
        "api_order": False,
        "auto_real_order": False,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    with open(RUNNER, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("=" * 60)
    print("ARGOS STOCK")
    print("STATUS : STOPPED")
    print("MODE : PAPER_ONLY")
    print("=" * 60)


if __name__ == "__main__":
    stop()