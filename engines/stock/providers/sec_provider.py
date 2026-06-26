from datetime import datetime


class SECProvider:

    def get(self):

        return {

            "provider": "SEC",

            "status": "READY",

            "market": "USA",

            "connected": False,

            "filings": [],

            "updated_at":
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        }


if __name__ == "__main__":

    print(SECProvider().get())