import json
from datetime import datetime

def run():
    return {
        "engine": "earnings_ai",
        "status": "READY",
        "mode": "PAPER_ONLY",
        "signal": "WAIT",
        "risk": "UNKNOWN",
        "summary": "US/KR earnings engine skeleton ready.",
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
