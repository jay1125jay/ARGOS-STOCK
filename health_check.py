import os

BASE_DIR = r"C:\ARGOS_STOCK"

CHECKS = [
    r"C:\ARGOS_STOCK\run_argos.py",
    r"C:\ARGOS_STOCK\app_server.py",
    r"C:\ARGOS_STOCK\engines\technical_engine.py",
    r"C:\ARGOS_STOCK\engines\position_manager.py",
    r"C:\ARGOS_STOCK\engines\risk_engine.py",
    r"C:\ARGOS_STOCK\engines\analytics_engine.py",
    r"C:\ARGOS_STOCK\engines\config_loader.py",
    r"C:\ARGOS_STOCK\engines\decision_logger.py",
    r"C:\ARGOS_STOCK\engines\cooldown_engine.py",
    r"C:\ARGOS_STOCK\config\settings.json",
    r"C:\ARGOS_STOCK\config\strategy.json",
    r"C:\ARGOS_STOCK\data\trades\paper_trades.csv",
    r"C:\ARGOS_STOCK\data\reports\report.csv",
    r"C:\ARGOS_STOCK\data\open_positions.json",
    r"C:\ARGOS_STOCK\data\cooldown.json"
]

def run_health_check():
    print("ARGOS HEALTH CHECK")
    print("=" * 40)

    ok = 0
    fail = 0

    for item in CHECKS:

        if os.path.exists(item):
            print(f"[OK] {item}")
            ok += 1
        else:
            print(f"[FAIL] {item}")
            fail += 1

    print("=" * 40)
    print(f"OK={ok}")
    print(f"FAIL={fail}")

if __name__ == "__main__":
    run_health_check()
