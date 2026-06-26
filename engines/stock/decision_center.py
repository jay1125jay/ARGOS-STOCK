import json
import os
from datetime import datetime

ROOT = r"C:\ARGOS_STOCK"

OUT = os.path.join(
    ROOT,
    "data",
    "decision",
    "final_decision.json"
)


class DecisionCenter:

    def evaluate(self, ai=None):

        signal = "WAIT"

        if ai:

            signal = ai.get("signal", "WAIT")

        result = {

            "project": "ARGOS_STOCK",

            "mode": "PAPER_ONLY",

            "real_order": False,

            "api_order": False,

            "auto_real_order": False,

            "signal": signal,

            "approved": signal in ["BUY", "SELL"],

            "updated_at":
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        }

        os.makedirs(os.path.dirname(OUT), exist_ok=True)

        with open(
            OUT,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                result,
                f,
                indent=2
            )

        return result


if __name__ == "__main__":

    dc = DecisionCenter()

    print(dc.evaluate())