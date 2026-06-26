import os
import csv
from datetime import datetime

ROOT = r"C:\ARGOS_STOCK"
TRADES_FILE = os.path.join(ROOT, "data", "trades", "paper_trades.csv")
REPORT_DIR = os.path.join(ROOT, "data", "reports")
ANALYSIS_FILE = os.path.join(REPORT_DIR, "argos_analysis.txt")

os.makedirs(REPORT_DIR, exist_ok=True)


def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def to_float(value, default=0.0):
    try:
        return float(str(value).replace("%", "").strip())
    except:
        return default


def read_trades():
    if not os.path.exists(TRADES_FILE):
        return []

    with open(TRADES_FILE, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main():
    print("ARGOS PERFORMANCE ANALYZER")
    print("MODE=PAPER_ONLY")
    print("-" * 60)

    trades = read_trades()

    if not trades:
        print("NO_TRADES_FOUND")
        return

    total_trades = len(trades)
    wins = 0
    losses = 0
    total_pnl = 0.0

    for row in trades:
        pnl = to_float(row.get("pnl", row.get("PNL", 0)))
        total_pnl += pnl

        if pnl > 0:
            wins += 1
        elif pnl < 0:
            losses += 1

    win_rate = (wins / total_trades) * 100 if total_trades > 0 else 0

    if total_trades < 10:
        status = "DATA_SHORT"
    elif win_rate >= 55 and total_pnl > 0:
        status = "GOOD"
    elif win_rate >= 45 and total_pnl >= 0:
        status = "WARNING"
    else:
        status = "BAD"

    last_trade = trades[-1]

    lines = []
    lines.append("ARGOS PERFORMANCE ANALYSIS")
    lines.append(f"LAST_RUN={now_text()}")
    lines.append(f"TOTAL_TRADES={total_trades}")
    lines.append(f"WINS={wins}")
    lines.append(f"LOSSES={losses}")
    lines.append(f"WIN_RATE={win_rate:.2f}%")
    lines.append(f"TOTAL_PNL={total_pnl:.6f}")
    lines.append(f"STATUS={status}")
    lines.append("-" * 60)
    lines.append("LAST_TRADE")
    for k, v in last_trade.items():
        lines.append(f"{k}={v}")

    text = "\n".join(lines)

    with open(ANALYSIS_FILE, "w", encoding="utf-8") as f:
        f.write(text)

    print(text)
    print("-" * 60)
    print("SAVED:", ANALYSIS_FILE)


if __name__ == "__main__":
    main()
