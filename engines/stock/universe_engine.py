import json
import os
from datetime import datetime

ROOT = r"C:\ARGOS_STOCK"
OUT = os.path.join(ROOT, "data", "universe", "universe_status.json")


class UniverseEngine:

    def now(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_symbols(self):
        return [
            "005930", "000660", "373220", "207940", "005380",
            "000270", "068270", "035420", "035720", "051910",
            "006400", "005490", "028260", "012330", "066570",
            "096770", "003550", "034020", "086790", "032830",
            "015760", "017670", "009540", "010130", "011200",
            "024110", "055550", "105560", "316140", "086280",
            "009150", "010950", "018260", "267260", "034730",
            "251270", "036570", "030200", "090430", "326030",
            "035250", "352820", "259960", "078930", "011070",
            "047050", "071050", "128940", "138040", "161390"
        ]

    def run(self):
        symbols = self.get_symbols()

        result = {
            "engine": "universe_engine",
            "status": "READY",
            "market": "KR",
            "count": len(symbols),
            "symbols": symbols,
            "updated_at": self.now()
        }

        os.makedirs(os.path.dirname(OUT), exist_ok=True)

        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        return result


if __name__ == "__main__":
    print(json.dumps(UniverseEngine().run(), indent=2, ensure_ascii=False))