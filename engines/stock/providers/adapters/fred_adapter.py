from datetime import datetime


class FREDAdapter:

    def connect(self):

        return {

            "provider": "FRED",

            "status": "READY",

            "connected": False,

            "paper_only": True,

            "macro": {},

            "updated_at":
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        }


if __name__ == "__main__":

    print(FREDAdapter().connect())