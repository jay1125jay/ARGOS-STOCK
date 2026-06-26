import os
import csv
import subprocess
from datetime import datetime

ROOT = r"C:\ARGOS_STOCK"
RUN_FILE = os.path.join(ROOT, "run_argos.py")
LOG_DIR = os.path.join(ROOT, "logs")
DATA_DIR = os.path.join(ROOT, "data")
REPORT_DIR = os.path.join(DATA_DIR, "reports")
TRADES_DIR = os.path.join(DATA_DIR, "trades")

REPORT_FILES = [
    os.path.join(REPORT_DIR, "report.csv"),
    os.path.join(TRADES_DIR, "paper_trades.csv"),
]

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)
os.makedirs(TRADES_DIR, exist_ok=True)


def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def save_log(name, text):
    path = os.path.join(LOG_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path


def check_csv(path):
    if not os.path.exists(path):
        return "MISSING"

    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            rows = list(csv.reader(f))

        if not rows:
            return "EMPTY"

        if len(rows[0]) < 2:
            return "BAD_HEADER"

        return "OK"

    except Exception as e:
        return "BROKEN: " + str(e)


def find_line_value(output, key):
    for line in output.splitlines():
        line = line.strip()
        if line.startswith(key + "="):
            return line.split("=", 1)[1].strip()
    return ""


def write_loop_status(output, failed):
    status_file = os.path.join(REPORT_DIR, "loop_status.txt")

    open_positions = find_line_value(output, "OPEN_POSITIONS")
    total_trades = find_line_value(output, "TOTAL_TRADES")
    wins = find_line_value(output, "WINS")
    losses = find_line_value(output, "LOSSES")
    win_rate = find_line_value(output, "WIN_RATE")
    total_pnl = find_line_value(output, "TOTAL_PNL")
    current_balance = find_line_value(output, "CURRENT_BALANCE")
    best_symbol = find_line_value(output, "BEST_SYMBOL")
    best_action = find_line_value(output, "BEST_ACTION")
    best_signal_score = find_line_value(output, "BEST_SIGNAL_SCORE")
    best_risk_score = find_line_value(output, "BEST_RISK_SCORE")

    with open(status_file, "w", encoding="utf-8") as f:
        f.write("ARGOS LOOP STATUS\n")
        f.write(f"RESULT={'FAIL' if failed else 'PASS'}\n")
        f.write(f"LAST_RUN={now_text()}\n")
        f.write(f"BEST_SYMBOL={best_symbol}\n")
        f.write(f"BEST_ACTION={best_action}\n")
        f.write(f"BEST_SIGNAL_SCORE={best_signal_score}\n")
        f.write(f"BEST_RISK_SCORE={best_risk_score}\n")
        f.write(f"OPEN_POSITIONS={open_positions}\n")
        f.write(f"TOTAL_TRADES={total_trades}\n")
        f.write(f"WINS={wins}\n")
        f.write(f"LOSSES={losses}\n")
        f.write(f"WIN_RATE={win_rate}\n")
        f.write(f"TOTAL_PNL={total_pnl}\n")
        f.write(f"CURRENT_BALANCE={current_balance}\n")

    return status_file


def main():
    print("ARGOS LOOP ENGINE")
    print("MODE=PAPER_ONLY")
    print("REAL_ORDER=FALSE")
    print("API_ORDER=FALSE")
    print("-" * 60)

    if not os.path.exists(RUN_FILE):
        print("FAIL: run_argos.py not found")
        return

    result = subprocess.run(
        ["py", RUN_FILE],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    output = ""
    output += "[TIME] " + now_text() + "\n"
    output += "[STDOUT]\n" + result.stdout + "\n"
    output += "[STDERR]\n" + result.stderr + "\n"

    log_name = "argos_loop_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".log"
    log_path = save_log(log_name, output)

    print(result.stdout)

    if result.stderr.strip():
        print("[STDERR]")
        print(result.stderr)

    failed = False

    if result.returncode != 0:
        failed = True
        print("FAIL: run_argos.py returned error code:", result.returncode)

    bad_words = [
        "Traceback",
        "ValueError",
        "TypeError",
        "KeyError",
        "IndexError",
        "ModuleNotFoundError",
        "FileNotFoundError",
    ]

    for word in bad_words:
        if word in output:
            failed = True
            print("FAIL DETECTED:", word)

    print("-" * 60)
    print("CSV CHECK")

    for path in REPORT_FILES:
        status = check_csv(path)
        print(status, path)

        if status.startswith("BROKEN") or status in ["EMPTY", "BAD_HEADER"]:
            failed = True

    status_file = write_loop_status(output, failed)

    print("-" * 60)
    print("LOG:", log_path)
    print("STATUS:", status_file)

    analyzer_file = os.path.join(ROOT, "analyze_argos.py")

    if os.path.exists(analyzer_file):
        analyzer_result = subprocess.run(
            ["py", analyzer_file],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

        print("-" * 60)
        print("ANALYZER RUN")
        print(analyzer_result.stdout)

        if analyzer_result.stderr.strip():
            print("[ANALYZER STDERR]")
            print(analyzer_result.stderr)
    else:
        print("ANALYZER=SKIPPED")

    if failed:
        print("RESULT=FAIL")
        print("NEXT: copy this screen and send it")
    else:
        print("RESULT=PASS")
        print("NEXT: check loop_status.txt")


if __name__ == "__main__":
    main()
