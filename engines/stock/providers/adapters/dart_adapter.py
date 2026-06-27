import json
import os
from datetime import datetime, timedelta

import requests

ROOT = r"C:\ARGOS_STOCK"
SECRET = os.path.join(ROOT, "config", "kis_secret.json")
OUT = os.path.join(ROOT, "data", "dart", "dart_cache.json")


class DARTAdapter:

    def load_json(self, path, default):
        if not os.path.exists(path):
            return default
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default

    def save_json(self, path, data):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def now(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def api_key(self):
        secret = self.load_json(SECRET, {})
        return secret.get("dart_api_key", "")

    def fetch(self):
        key = self.api_key()

        if not key:
            return {
                "provider": "DART",
                "status": "MOCK_READY",
                "connected": False,
                "paper_only": True,
                "market": "KOREA",
                "disclosures": [],
                "updated_at": self.now()
            }

        end = datetime.now()
        start = end - timedelta(days=3)

        params = {
            "crtfc_key": key,
            "bgn_de": start.strftime("%Y%m%d"),
            "end_de": end.strftime("%Y%m%d"),
            "page_count": 100
        }

        try:
            res = requests.get(
                "https://opendart.fss.or.kr/api/list.json",
                params=params,
                timeout=10
            )

            if res.status_code != 200:
                return {
                    "provider": "DART",
                    "status": "DART_FAIL",
                    "connected": False,
                    "paper_only": True,
                    "market": "KOREA",
                    "disclosures": [],
                    "message": res.text,
                    "updated_at": self.now()
                }

            data = res.json()
            disclosures = data.get("list", [])

            return {
                "provider": "DART",
                "status": "REAL_READY",
                "connected": True,
                "paper_only": True,
                "market": "KOREA",
                "disclosures": disclosures,
                "updated_at": self.now()
            }

        except Exception as e:
            return {
                "provider": "DART",
                "status": "DART_ERROR",
                "connected": False,
                "paper_only": True,
                "market": "KOREA",
                "disclosures": [],
                "message": str(e),
                "updated_at": self.now()
            }

    def connect(self):
        result = self.fetch()
        self.save_json(OUT, result)
        return result


if __name__ == "__main__":
    print(json.dumps(DARTAdapter().connect(), indent=2, ensure_ascii=False))