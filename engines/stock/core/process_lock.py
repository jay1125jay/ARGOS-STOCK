import json
import os
from datetime import datetime

ROOT = r"C:\ARGOS_STOCK"

LOCK_FILE = os.path.join(
    ROOT,
    "data",
    "system",
    "process.lock"
)


class ProcessLock:

    def __init__(self):
        os.makedirs(
            os.path.dirname(LOCK_FILE),
            exist_ok=True
        )

    def process_exists(self, pid):
        try:
            pid = int(pid)

            if pid <= 0:
                return False

            os.kill(pid, 0)
            return True

        except Exception:
            return False

    def load_lock(self):
        if not os.path.exists(LOCK_FILE):
            return {}

        try:
            with open(
                LOCK_FILE,
                "r",
                encoding="utf-8"
            ) as f:
                data = json.load(f)

            return data if isinstance(data, dict) else {}

        except Exception:
            return {}

    def remove_stale_lock(self):
        if not os.path.exists(LOCK_FILE):
            return False

        lock_data = self.load_lock()
        pid = lock_data.get("pid", 0)

        if pid and self.process_exists(pid):
            return False

        try:
            os.remove(LOCK_FILE)
            print("STALE_LOCK_REMOVED")
            return True

        except Exception:
            return False

    def acquire(self):
        if os.path.exists(LOCK_FILE):
            self.remove_stale_lock()

        if os.path.exists(LOCK_FILE):
            return False

        lock_data = {
            "locked": True,
            "pid": os.getpid(),
            "started_at": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        }

        try:
            with open(
                LOCK_FILE,
                "x",
                encoding="utf-8"
            ) as f:
                json.dump(
                    lock_data,
                    f,
                    ensure_ascii=False,
                    indent=2
                )

            return True

        except FileExistsError:
            return False

        except Exception:
            return False

    def release(self):
        if not os.path.exists(LOCK_FILE):
            return

        lock_data = self.load_lock()
        lock_pid = lock_data.get("pid", 0)

        if lock_pid and int(lock_pid) != os.getpid():
            return

        try:
            os.remove(LOCK_FILE)
        except Exception:
            pass

    def is_running(self):
        if not os.path.exists(LOCK_FILE):
            return False

        lock_data = self.load_lock()
        pid = lock_data.get("pid", 0)

        if pid and self.process_exists(pid):
            return True

        self.remove_stale_lock()
        return False


if __name__ == "__main__":
    lock = ProcessLock()

    if lock.acquire():
        print("LOCK_CREATED")
        print("PID :", os.getpid())
        lock.release()
        print("LOCK_RELEASED")
    else:
        print("ALREADY_RUNNING")