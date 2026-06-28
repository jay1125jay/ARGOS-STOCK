def latest_rsi(values, period=14):
    if not values or len(values) < period + 1:
        return 50

    gains = []
    losses = []

    for i in range(1, len(values)):
        diff = float(values[i]) - float(values[i - 1])
        gains.append(max(diff, 0))
        losses.append(abs(min(diff, 0)))

    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return round(rsi, 2)