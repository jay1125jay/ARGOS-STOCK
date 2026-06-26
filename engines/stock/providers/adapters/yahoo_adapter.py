from datetime import datetime


class YahooAdapter:

    def connect(self):

        return {

            "provider": "Yahoo",

            "status": "READY",

            "connected": False,

            "paper_only": True,

            "symbols": [],

            "updated_at":
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        }


if __name__ == "__main__":

    print(YahooAdapter().connect())