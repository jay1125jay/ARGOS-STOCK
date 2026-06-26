from datetime import datetime


class SECAdapter:

    def connect(self):

        return {
            "provider": "SEC",
            "status": "READY",
            "connected": False,
            "paper_only": True,
            "market": "USA",
            "filings": [],
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


if __name__ == "__main__":

    print(SECAdapter().connect())