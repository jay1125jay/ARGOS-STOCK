def latest_atr(candles, period=14):
    if not candles or len(candles) < period + 1:
        return 0

    true_ranges = []

    for i in range(1, len(candles)):
        high = float(candles[i].get("high", 0))
        low = float(candles[i].get("low", 0))
        prev_close = float(candles[i - 1].get("close", 0))

        tr = max(
            high - low,
            abs(high - prev_close),
            abs(low - prev_close)
        )

        true_ranges.append(tr)

    recent = true_ranges[-period:]

    if not recent:
        return 0

    return round(sum(recent) / len(recent), 4)