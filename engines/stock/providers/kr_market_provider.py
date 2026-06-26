from datetime import datetime


class KRMarketProvider:

    def get(self):

        return {

            "provider": "KR_MARKET",

            "status": "READY",

            "market": "KOREA",

            "connected": False,

            "symbols": [],

            "updated_at":
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        }


if __name__ == "__main__":

    print(KRMarketProvider().get())