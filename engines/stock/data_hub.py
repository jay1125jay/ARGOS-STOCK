import json
import os
from datetime import datetime

ROOT = r"C:\ARGOS_STOCK"

STATUS = os.path.join(
    ROOT,
    "data",
    "stock",
    "data_hub_status.json"
)


class DataHub:

    def __init__(self):

        self.mode = "PAPER_ONLY"

    def build(self):

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return {

            "project": "ARGOS_STOCK",

            "mode": self.mode,

            "real_order": False,

            "api_order": False,

            "auto_real_order": False,

            "updated_at": now,

            "market": {

                "kr": "READY",

                "us": "READY"

            },

            "sources": {

                "news": "READY",

                "dart": "READY",

                "sec": "READY",

                "earnings": "READY",

                "sector": "READY",

                "money_flow": "READY",

                "macro": "READY",

                "fx": "READY",

                "vix": "READY"

            }

        }

    def save(self):

        os.makedirs(os.path.dirname(STATUS), exist_ok=True)

        data = self.build()

        with open(
            STATUS,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                indent=2
            )

        return data


if __name__ == "__main__":

    hub = DataHub()

    hub.save()

    print("DATA HUB READY")