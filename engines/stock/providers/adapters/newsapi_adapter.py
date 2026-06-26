from datetime import datetime


class NewsAPIAdapter:

    def connect(self):

        return {

            "provider": "NewsAPI",

            "status": "READY",

            "connected": False,

            "paper_only": True,

            "articles": [],

            "updated_at":
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        }


if __name__ == "__main__":

    print(NewsAPIAdapter().connect())