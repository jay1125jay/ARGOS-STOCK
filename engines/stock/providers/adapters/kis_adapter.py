from datetime import datetime


class KISAdapter:

    def connect(self):

        return {

            "provider": "KIS",

            "status": "READY",

            "connected": False,

            "paper_only": True,

            "market": "KOREA",

            "symbols": [],

            "updated_at":
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        }


if __name__ == "__main__":

    print(KISAdapter().connect())