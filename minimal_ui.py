import tkinter as tk
from tkinter import ttk
import subprocess
import sys

ROOT = r"C:\ARGOS_STOCK"

runner = None


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

    status_var.set("STOPPED")


def auto():

    subprocess.run(
        [sys.executable, "auto_mode.py"],
        cwd=ROOT
    )


root = tk.Tk()

root.title("ARGOS STOCK")

root.geometry("420x600")

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

ttk.Button(
    root,
    text="START",
    command=start
).pack(fill="x", padx=40, pady=10)

ttk.Button(
    root,
    text="STOP",
    command=stop
).pack(fill="x", padx=40, pady=10)

ttk.Button(
    root,
    text="AUTO",
    command=auto
).pack(fill="x", padx=40, pady=10)

ttk.Button(
    root,
    text="HISTORY"
).pack(fill="x", padx=40, pady=10)

ttk.Button(
    root,
    text="SETTINGS"
).pack(fill="x", padx=40, pady=10)

root.mainloop()