from datetime import datetime


class DARTProvider:

    def get(self):

        return {

            "provider": "DART",

            "status": "READY",

            "market": "KOREA",

            "connected": False,

            "disclosures": [],

            "updated_at":
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        }


if __name__ == "__main__":

    print(DARTProvider().get())