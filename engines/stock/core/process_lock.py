import os
import json
from datetime import datetime

ROOT = r"C:\ARGOS_STOCK"

LOCK_FILE = os.path.join(ROOT, "data", "system", "process.lock")


class ProcessLock:

    def __init__(self):
        os.makedirs(os.path.dirname(LOCK_FILE), exist_ok=True)

    def acquire(self):

        if os.path.exists(LOCK_FILE):
            return False

        with open(LOCK_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "locked": True,
                "started_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }, f, indent=2)

        return True

    def release(self):

        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)

    def is_running(self):

        return os.path.exists(LOCK_FILE)


if __name__ == "__main__":

    lock = ProcessLock()

    if lock.acquire():
        print("LOCK_CREATED")
    else:
        print("ALREADY_RUNNING")