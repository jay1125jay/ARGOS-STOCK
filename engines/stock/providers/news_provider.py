from datetime import datetime


class NewsProvider:

    def get(self):

        return {

            "provider": "NEWS",

            "status": "READY",

            "connected": False,

            "source": "NONE",

            "articles": [],

            "updated_at":
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        }


if __name__ == "__main__":

    print(NewsProvider().get())