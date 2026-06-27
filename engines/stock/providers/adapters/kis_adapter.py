import json
import os
import time
from datetime import datetime

import requests


ROOT = r"C:\ARGOS_STOCK"
KIS_CONFIG = os.path.join(ROOT, "config", "kis_config.json")
KIS_SECRET = os.path.join(ROOT, "config", "kis_secret.json")
STOCK_SETTINGS = os.path.join(ROOT, "config", "stock", "stock_settings.json")
KIS_CACHE = os.path.join(ROOT, "data", "stock", "kis_cache.json")
KIS_TOKEN = os.path.join(ROOT, "data", "stock", "kis_token.json")


class KISAdapter:
    def __init__(self):
        self.config = self.load_json(KIS_CONFIG, {})
        self.secret = self.load_json(KIS_SECRET, {})
        self.settings = self.load_json(STOCK_SETTINGS, {})
        self.kis = self.config.get("kis", {})

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

    def app_key(self):
        return self.secret.get("app_key", "") or self.kis.get("app_key", "")

    def app_secret(self):
        return self.secret.get("app_secret", "") or self.kis.get("app_secret", "")

    def base_url(self):
        return self.kis.get(
            "base_url",
            "https://openapivts.koreainvestment.com:29443"
        )

    def has_keys(self):
        return bool(self.app_key()) and bool(self.app_secret())

    def get_token(self):
        if os.path.exists(KIS_TOKEN):
            token_data = self.load_json(KIS_TOKEN, {})

            if token_data.get("status") == "TOKEN_OK":
                token = token_data.get("access_token", "")

                if token:
                    return token

        if not self.has_keys():
            return ""

        url = self.base_url().rstrip("/") + "/oauth2/tokenP"

        headers = {
            "content-type": "application/json"
        }

        body = {
            "grant_type": "client_credentials",
            "appkey": self.app_key(),
            "appsecret": self.app_secret()
        }

        try:
            res = requests.post(
                url,
                headers=headers,
                data=json.dumps(body),
                timeout=10
            )

            if res.status_code != 200:
                self.save_json(KIS_TOKEN, {
                    "status": "TOKEN_FAIL",
                    "status_code": res.status_code,
                    "message": res.text,
                    "updated_at": self.now()
                })
                return ""

            data = res.json()
            token = data.get("access_token", "")

            self.save_json(KIS_TOKEN, {
                "status": "TOKEN_OK" if token else "TOKEN_EMPTY",
                "access_token": token,
                "token_type": data.get("token_type", ""),
                "expires_in": data.get("expires_in", ""),
                "expired_at": data.get("access_token_token_expired", ""),
                "updated_at": self.now()
            })

            return token

        except Exception as e:
            self.save_json(KIS_TOKEN, {
                "status": "TOKEN_ERROR",
                "message": str(e),
                "updated_at": self.now()
            })
            return ""

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
            "status": "MOCK_READY",
            "updated_at": self.now()
        }

    def get_domestic_quote(self, token, symbol):
        url = (
            self.base_url().rstrip("/")
            + "/uapi/domestic-stock/v1/quotations/inquire-price"
        )

        headers = {
            "content-type": "application/json; charset=utf-8",
            "authorization": "Bearer " + token,
            "appkey": self.app_key(),
            "appsecret": self.app_secret(),
            "tr_id": "FHKST01010100"
        }

        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": symbol
        }

        try:
            res = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=10
            )

            if res.status_code != 200:
                return {
                    "symbol": symbol,
                    "status": "QUOTE_FAIL",
                    "status_code": res.status_code,
                    "message": res.text,
                    "source": "KIS_REAL",
                    "updated_at": self.now()
                }

            data = res.json()
            output = data.get("output", {})

            return {
                "symbol": symbol,
                "name": output.get("hts_kor_isnm", ""),
                "price": float(output.get("stck_prpr", 0) or 0),
                "change_rate": float(output.get("prdy_ctrt", 0) or 0),
                "volume": int(float(output.get("acml_vol", 0) or 0)),
                "bid": float(output.get("bidp", 0) or 0),
                "ask": float(output.get("askp", 0) or 0),
                "source": "KIS_REAL",
                "status": "QUOTE_OK",
                "raw": output,
                "updated_at": self.now()
            }

        except Exception as e:
            return {
                "symbol": symbol,
                "status": "QUOTE_ERROR",
                "message": str(e),
                "source": "KIS_REAL",
                "updated_at": self.now()
            }

    def collect_watchlist(self):
        watchlist = self.settings.get("kr_watchlist", [])
        quotes = []

        if not self.has_keys():
            for symbol in watchlist:
                quotes.append(self.mock_quote(symbol))

            status = "MOCK_READY"
            connected = False
            mock_mode = True

        else:
            token = self.get_token()

            if not token:
                for symbol in watchlist:
                    quotes.append(self.mock_quote(symbol))

                status = "TOKEN_FAIL_FALLBACK_MOCK"
                connected = False
                mock_mode = True

            else:
                for symbol in watchlist:
                    quotes.append(self.get_domestic_quote(token, symbol))
                    time.sleep(1.1)

                status = "REAL_READY"
                connected = True
                mock_mode = False

        payload = {
            "project": "ARGOS_STOCK",
            "mode": "PAPER_ONLY",
            "real_order": False,
            "api_order": False,
            "auto_real_order": False,
            "provider": "KIS",
            "mock_mode": mock_mode,
            "connected": connected,
            "status": status,
            "market": "KOREA",
            "symbols": watchlist,
            "quotes": quotes,
            "updated_at": self.now()
        }

        self.save_json(KIS_CACHE, payload)
        return payload

    def connect(self):
        data = self.collect_watchlist()

        return {
            "provider": "KIS",
            "status": data.get("status", "UNKNOWN"),
            "connected": data.get("connected", False),
            "paper_only": True,
            "real_order": False,
            "api_order": False,
            "auto_real_order": False,
            "market": "KOREA",
            "symbols": data.get("symbols", []),
            "cache": KIS_CACHE,
            "updated_at": self.now()
        }


if __name__ == "__main__":
    adapter = KISAdapter()
    print(json.dumps(adapter.connect(), indent=2, ensure_ascii=False))