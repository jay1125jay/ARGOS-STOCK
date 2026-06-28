from engines.stock.indicators.ema import ema


def latest_macd(values, fast=12, slow=26, signal=9):
    if not values or len(values) < slow + signal:
        return {
            "macd": 0,
            "signal": 0,
            "histogram": 0
        }

    fast_ema = ema(values, fast)
    slow_ema = ema(values, slow)

    macd_line = []

    for i in range(len(values)):
        if i < len(fast_ema) and i < len(slow_ema):
            macd_line.append(fast_ema[i] - slow_ema[i])

    signal_line = ema(macd_line, signal)

    if not macd_line or not signal_line:
        return {
            "macd": 0,
            "signal": 0,
            "histogram": 0
        }

    macd_value = macd_line[-1]
    signal_value = signal_line[-1]

    return {
        "macd": round(macd_value, 4),
        "signal": round(signal_value, 4),
        "histogram": round(macd_value - signal_value, 4)
    }