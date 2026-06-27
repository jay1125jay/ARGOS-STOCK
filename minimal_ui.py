import csv
import json
import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, messagebox

ROOT = r"C:\ARGOS_STOCK"

RUNNER_STATUS = os.path.join(ROOT, "data", "runner", "runner_status.json")
TRADES_CSV = os.path.join(ROOT, "data", "trades", "paper_trades.csv")
PROVIDERS_JSON = os.path.join(ROOT, "config", "providers.json")
STOCK_SETTINGS = os.path.join(ROOT, "config", "stock", "stock_settings.json")
AUTO_JSON = os.path.join(ROOT, "data", "auto", "auto_mode.json")

runner = None


def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def refresh_status():
    data = load_json(RUNNER_STATUS, {})

    status_var.set("RUNNING" if data.get("running") else "STOPPED")
    ai_var.set(data.get("ai_signal", "WAIT"))
    final_var.set(data.get("final_signal", "WAIT"))
    account_var.set(str(data.get("account", 10000000)))
    position_var.set(str(data.get("positions", 0)))
    history_var.set(str(data.get("history", 0)))
    update_var.set(data.get("updated_at", "-"))

    root.after(1000, refresh_status)


def start():
    global runner

    if runner is None:
        runner = subprocess.Popen(
            [sys.executable, "start.py"],
            cwd=ROOT
        )

    status_var.set("RUNNING")


def stop():
    global runner

    if runner:
        runner.terminate()
        runner = None

    subprocess.run(
        [sys.executable, "stop.py"],
        cwd=ROOT
    )

    refresh_status()


def auto():
    data = load_json(AUTO_JSON, {"auto_mode": False})
    new_value = not bool(data.get("auto_mode"))

    payload = {
        "project": "ARGOS_STOCK",
        "mode": "PAPER_ONLY",
        "auto_mode": new_value,
        "real_order": False,
        "api_order": False,
        "auto_real_order": False
    }

    save_json(AUTO_JSON, payload)

    messagebox.showinfo(
        "AUTO MODE",
        "AUTO MODE : ON" if new_value else "AUTO MODE : OFF"
    )


def history():
    if not os.path.exists(TRADES_CSV):
        messagebox.showinfo("HISTORY", "NO PAPER TRADES")
        return

    with open(TRADES_CSV, "r", encoding="utf-8") as f:
        rows = list(csv.reader(f))

    total = max(len(rows) - 1, 0)

    messagebox.showinfo(
        "HISTORY",
        f"TOTAL TRADES : {total}"
    )


def settings():
    providers = load_json(PROVIDERS_JSON, {})
    stock = load_json(STOCK_SETTINGS, {})

    kr_provider = providers.get("kr_market", {}).get("provider", "UNKNOWN")
    us_provider = providers.get("us_market", {}).get("provider", "UNKNOWN")
    watchlist = len(stock.get("kr_watchlist", []))

    text = (
        "MODE : PAPER_ONLY\n"
        "REAL_ORDER : FALSE\n"
        "API_ORDER : FALSE\n"
        "AUTO_REAL_ORDER : FALSE\n\n"
        f"KR PROVIDER : {kr_provider}\n"
        f"US PROVIDER : {us_provider}\n"
        f"KR WATCHLIST : {watchlist}"
    )

    messagebox.showinfo("SETTINGS", text)


root = tk.Tk()
root.title("ARGOS STOCK")
root.geometry("420x680")
root.resizable(False, False)

ttk.Label(
    root,
    text="ARGOS STOCK",
    font=("Arial", 20, "bold")
).pack(pady=20)

status_var = tk.StringVar(value="STOPPED")

ttk.Label(
    root,
    textvariable=status_var,
    font=("Arial", 14)
).pack()

ttk.Separator(root).pack(fill="x", pady=20)

ttk.Button(root, text="START", command=start).pack(fill="x", padx=40, pady=8)
ttk.Button(root, text="STOP", command=stop).pack(fill="x", padx=40, pady=8)
ttk.Button(root, text="AUTO", command=auto).pack(fill="x", padx=40, pady=8)
ttk.Button(root, text="HISTORY", command=history).pack(fill="x", padx=40, pady=8)
ttk.Button(root, text="SETTINGS", command=settings).pack(fill="x", padx=40, pady=8)

ttk.Separator(root).pack(fill="x", pady=20)

ai_var = tk.StringVar(value="WAIT")
final_var = tk.StringVar(value="WAIT")
account_var = tk.StringVar(value="10000000")
position_var = tk.StringVar(value="0")
history_var = tk.StringVar(value="0")
update_var = tk.StringVar(value="-")

info = ttk.Frame(root)
info.pack(fill="x", padx=40)

rows = [
    ("AI SIGNAL", ai_var),
    ("FINAL SIGNAL", final_var),
    ("ACCOUNT", account_var),
    ("POSITIONS", position_var),
    ("HISTORY", history_var),
    ("LAST UPDATE", update_var),
]

for label, var in rows:
    ttk.Label(info, text=label).pack(anchor="w")
    ttk.Label(info, textvariable=var, font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 8))

refresh_status()
root.mainloop()