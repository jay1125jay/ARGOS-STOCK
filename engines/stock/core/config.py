import os


class Config:
    ROOT = r"C:\ARGOS_STOCK"

    DATA = os.path.join(ROOT, "data")
    REPORTS = os.path.join(ROOT, "reports")
    LOGS = os.path.join(ROOT, "logs")
    API = os.path.join(ROOT, "api")

    API_HOST = "127.0.0.1"
    API_PORT = 8000

    PROJECT = "ARGOS_STOCK"
    MODE = "PAPER_ONLY"

    PAPER_ONLY = True
    REAL_ORDER = False
    API_ORDER = False
    AUTO_REAL_ORDER = False

    @staticmethod
    def path(*parts):
        return os.path.join(Config.ROOT, *parts)

    @staticmethod
    def data_path(*parts):
        return os.path.join(Config.DATA, *parts)

    @staticmethod
    def report_path(*parts):
        return os.path.join(Config.REPORTS, *parts)

    @staticmethod
    def log_path(*parts):
        return os.path.join(Config.LOGS, *parts)

    @staticmethod
    def ensure_dirs():
        os.makedirs(Config.DATA, exist_ok=True)
        os.makedirs(Config.REPORTS, exist_ok=True)
        os.makedirs(Config.LOGS, exist_ok=True)
        os.makedirs(Config.API, exist_ok=True)


if __name__ == "__main__":
    Config.ensure_dirs()

    print("CONFIG_READY")
    print("ROOT:", Config.ROOT)
    print("MODE:", Config.MODE)
    print("API:", f"{Config.API_HOST}:{Config.API_PORT}")
    print("PAPER_ONLY:", Config.PAPER_ONLY)
    print("REAL_ORDER:", Config.REAL_ORDER)