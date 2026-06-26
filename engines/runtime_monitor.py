import json
import os
from datetime import datetime

BASE_DIR = r"C:\ARGOS_AI"
RUNTIME_FILE = os.path.join(BASE_DIR, "data", "system", "runtime_status.json")


def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def runtime_text(seconds):
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def default_runtime():
    return {
        "engine": "ARGOS_RUNTIME_MONITOR_V30",
        "status": "RUNNING",
        "started_at": now_text(),
        "last_update": now_text(),
        "runtime_seconds": 0,
        "runtime_text": "00:00:00",
        "loops": 0,
        "health": "GOOD",
        "last_error": "",
        "paper_mode": True,
        "real_order_enabled": False,
        "api_order_enabled": False,
        "auto_real_order_enabled": False
    }

    update_runtime_status(health="GOOD", last_error="")

    if not data.get("started_at"):
        data["started_at"] = now_text()

    if not data.get("last_update"):
        data["last_update"] = now_text()

    start = datetime.strptime(data["started_at"], "%Y-%m-%d %H:%M:%S")
    now = datetime.now()
    seconds = int((now - start).total_seconds())

    data["status"] = "RUNNING"
    data["last_update"] = now_text()
    data["runtime_seconds"] = seconds
    data["runtime_text"] = runtime_text(seconds)

    if loops is None:
        data["loops"] = int(data.get("loops", 0)) + 1
    else:
        data["loops"] = int(loops)

    data["health"] = health
    data["last_error"] = last_error
    data["paper_mode"] = True
    data["real_order_enabled"] = False
    data["api_order_enabled"] = False
    data["auto_real_order_enabled"] = False

    save_json(RUNTIME_FILE, data)
    return data