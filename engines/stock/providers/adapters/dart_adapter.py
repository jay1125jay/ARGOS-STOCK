from datetime import datetime


class DARTAdapter:

    def connect(self):

        return {

            "provider": "DART",

            "status": "READY",

            "connected": False,

            "paper_only": True,

            "market": "KOREA",

            "disclosures": [],

            "updated_at":
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        }


if __name__ == "__main__":

    print(DARTAdapter().connect())