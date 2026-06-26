from datetime import datetime


class USMarketProvider:

    def get(self):

        return {

            "provider": "US_MARKET",

            "status": "READY",

            "market": "USA",

            "connected": False,

            "symbols": [],

            "updated_at":
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        }


if __name__ == "__main__":

    print(USMarketProvider().get())