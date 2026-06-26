import json
import os
from datetime import datetime

ROOT = r"C:\ARGOS_STOCK"

AUTO = os.path.join(
    ROOT,
    "data",
    "auto",
    "auto_mode.json"
)


def enable():

    os.makedirs(os.path.dirname(AUTO), exist_ok=True)

    data = {
        "project": "ARGOS_STOCK",
        "mode": "PAPER_ONLY",
        "auto_mode": True,
        "real_order": False,
        "api_order": False,
        "auto_real_order": False,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    with open(AUTO, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("=" * 60)
    print("AUTO MODE : ON")
    print("PAPER ONLY")
    print("=" * 60)


def disable():

    os.makedirs(os.path.dirname(AUTO), exist_ok=True)

    data = {
        "project": "ARGOS_STOCK",
        "mode": "PAPER_ONLY",
        "auto_mode": False,
        "real_order": False,
        "api_order": False,
        "auto_real_order": False,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    with open(AUTO, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("=" * 60)
    print("AUTO MODE : OFF")
    print("PAPER ONLY")
    print("=" * 60)


if __name__ == "__main__":
    enable()