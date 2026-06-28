def ema(values, period):
    if not values or period <= 0:
        return []

    result = []
    k = 2 / (period + 1)
    prev = float(values[0])
    result.append(prev)

    for v in values[1:]:
        v = float(v)
        current = (v * k) + (prev * (1 - k))
        result.append(round(current, 4))
        prev = current

    return result


def latest_ema(values, period):
    data = ema(values, period)
    return data[-1] if data else 0