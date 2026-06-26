import json
import os
from datetime import datetime

ROOT = r"C:\ARGOS_STOCK"
CACHE = os.path.join(ROOT, "data", "stock", "provider_cache.json")


class DataCache:

    def save(self, data):

        os.makedirs(os.path.dirname(CACHE), exist_ok=True)

        payload = {
            "project": "ARGOS_STOCK",
            "mode": "PAPER_ONLY",
            "real_order": False,
            "api_order": False,
            "auto_real_order": False,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data": data
        }

        with open(CACHE, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

        return payload

    def load(self):

        if not os.path.exists(CACHE):
            return {}

        with open(CACHE, "r", encoding="utf-8") as f:
            return json.load(f)


if __name__ == "__main__":

    cache = DataCache()

    cache.save({
        "status": "READY"
    })

    print("DATA CACHE READY")