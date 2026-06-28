import json
import os
from datetime import datetime

from engines.stock.indicators.ema import latest_ema
from engines.stock.indicators.rsi import latest_rsi
from engines.stock.indicators.macd import latest_macd
from engines.stock.indicators.atr import latest_atr

ROOT = r"C:\ARGOS_STOCK"

HISTORY_DIR = os.path.join(ROOT, "data", "history")
OUT = os.path.join(ROOT, "data", "indicator", "indicator_status.json")


class IndicatorEngine:

    def now(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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

    def list_history_files(self):
        if not os.path.exists(HISTORY_DIR):
            return []

        files = []

        for name in os.listdir(HISTORY_DIR):
            if name.endswith("_history.json"):
                files.append(os.path.join(HISTORY_DIR, name))

        return files

    def analyze_symbol(self, path):
        data = self.load_json(path, {})
        symbol = data.get("symbol", "")
        candles = data.get("candles", [])

        closes = [float(x.get("close", 0) or 0) for x in candles]

        ema5 = latest_ema(closes, 5)
        ema20 = latest_ema(closes, 20)
        ema60 = latest_ema(closes, 60)
        rsi14 = latest_rsi(closes, 14)
        macd = latest_macd(closes)
        atr14 = latest_atr(candles, 14)

        score = 0
        reasons = []

        if ema5 > ema20 > ema60:
            score += 30
            reasons.append("EMA_UP_TREND")
        elif ema5 < ema20 < ema60:
            score -= 30
            reasons.append("EMA_DOWN_TREND")
        else:
            reasons.append("EMA_MIXED")

        if 50 <= rsi14 <= 70:
            score += 15
            reasons.append("RSI_HEALTHY")
        elif rsi14 > 80:
            score -= 15
            reasons.append("RSI_OVERBOUGHT")
        elif rsi14 < 30:
            score -= 10
            reasons.append("RSI_WEAK")
        else:
            reasons.append("RSI_NEUTRAL")

        if macd.get("histogram", 0) > 0:
            score += 15
            reasons.append("MACD_POSITIVE")
        elif macd.get("histogram", 0) < 0:
            score -= 15
            reasons.append("MACD_NEGATIVE")
        else:
            reasons.append("MACD_FLAT")

        if atr14 > 0:
            score += 5
            reasons.append("ATR_OK")
        else:
            reasons.append("ATR_NONE")

        signal = "WAIT"

        if score >= 50:
            signal = "BUY"
        elif score <= -50:
            signal = "SELL"

        return {
            "symbol": symbol,
            "signal": signal,
            "score": score,
            "ema5": ema5,
            "ema20": ema20,
            "ema60": ema60,
            "rsi14": rsi14,
            "macd": macd,
            "atr14": atr14,
            "reason": ",".join(reasons)
        }

    def run(self):
        files = self.list_history_files()
        items = []

        for path in files:
            result = self.analyze_symbol(path)

            if result.get("symbol"):
                items.append(result)

        ranked = sorted(
            items,
            key=lambda x: x.get("score", 0),
            reverse=True
        )

        best = ranked[0] if ranked else {}

        result = {
            "engine": "indicator_engine",
            "status": "READY" if items else "NO_HISTORY",
            "mode": "PAPER_ONLY",
            "count": len(items),
            "best": best,
            "top20": ranked[:20],
            "items": ranked,
            "updated_at": self.now()
        }

        self.save_json(OUT, result)
        return result


def run():
    return IndicatorEngine().run()


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))