import json
import os
from datetime import datetime


ROOT = r"C:\ARGOS_STOCK"
KIS_CONFIG = os.path.join(ROOT, "config", "kis_config.json")
STOCK_SETTINGS = os.path.join(ROOT, "config", "stock", "stock_settings.json")
KIS_CACHE = os.path.join(ROOT, "data", "stock", "kis_cache.json")


class KISAdapter:
    def __init__(self):
        self.config = self.load_json(KIS_CONFIG, {})
        self.settings = self.load_json(STOCK_SETTINGS, {})

    def load_json(self, path, default):
        if not os.path.exists(path):
            return default
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_json(self, path, data):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def has_keys(self):
        kis = self.config.get("kis", {})
        return bool(kis.get("app_key")) and bool(kis.get("app_secret"))

    def mock_quote(self, symbol):
        return {
            "symbol": symbol,
            "name": "MOCK_KR_STOCK",
            "price": 70000,
            "change_rate": 0.0,
            "volume": 1000000,
            "bid": 69900,
            "ask": 70100,
            "source": "KIS_MOCK",
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def collect_watchlist(self):
        watchlist = self.settings.get("kr_watchlist", [])

        quotes = []
        for symbol in watchlist:
            quotes.append(self.mock_quote(symbol))

        payload = {
            "project": "ARGOS_STOCK",
            "mode": "PAPER_ONLY",
            "real_order": False,
            "api_order": False,
            "auto_real_order": False,
            "provider": "KIS",
            "mock_mode": not self.has_keys(),
            "status": "MOCK_READY" if not self.has_keys() else "KEY_READY",
            "market": "KOREA",
            "symbols": watchlist,
            "quotes": quotes,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.save_json(KIS_CACHE, payload)
        return payload

    def connect(self):
        data = self.collect_watchlist()

        return {
            "provider": "KIS",
            "status": data.get("status", "MOCK_READY"),
            "connected": self.has_keys(),
            "paper_only": True,
            "real_order": False,
            "api_order": False,
            "auto_real_order": False,
            "market": "KOREA",
            "symbols": data.get("symbols", []),
            "cache": KIS_CACHE,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


if __name__ == "__main__":
    adapter = KISAdapter()
    print(json.dumps(adapter.connect(), indent=2, ensure_ascii=False))