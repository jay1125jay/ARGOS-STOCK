import json
import os

BASE_DIR = r"C:\ARGOS_AI"
RUNTIME_FILE = os.path.join(BASE_DIR, "data", "system", "runtime_status.json")


def read_json(path):
    if not os.path.exists(path):
        return {}

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    data = read_json(RUNTIME_FILE)

    print("ARGOS V30 RUNTIME CHECK")
    print("=" * 60)
    print("RUNTIME_ENGINE=" + str(data.get("engine", "-")))
    print("STATUS=" + str(data.get("status", "-")))
    print("RUNTIME=" + str(data.get("runtime_text", "-")))
    print("LOOPS=" + str(data.get("loops", 0)))
    print("LAST_UPDATE=" + str(data.get("last_update", "-")))
    print("HEALTH=" + str(data.get("health", "-")))
    print("LAST_ERROR=" + str(data.get("last_error", "")))
    print("=" * 60)

    if data.get("engine") == "ARGOS_RUNTIME_MONITOR_V30":
        print("V30_RUNTIME=PASS")
    else:
        print("V30_RUNTIME=CHECK_REQUIRED")


if __name__ == "__main__":
    main()