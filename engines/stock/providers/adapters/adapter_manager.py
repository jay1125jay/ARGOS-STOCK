from engines.stock.providers.adapters.yahoo_adapter import YahooAdapter
from engines.stock.providers.adapters.kis_adapter import KISAdapter
from engines.stock.providers.adapters.newsapi_adapter import NewsAPIAdapter
from engines.stock.providers.adapters.dart_adapter import DARTAdapter
from engines.stock.providers.adapters.sec_adapter import SECAdapter
from engines.stock.providers.adapters.fred_adapter import FREDAdapter


class AdapterManager:

    def __init__(self):

        self.yahoo = YahooAdapter()
        self.kis = KISAdapter()
        self.news = NewsAPIAdapter()
        self.dart = DARTAdapter()
        self.sec = SECAdapter()
        self.fred = FREDAdapter()

    def connect(self):

        return {

            "yahoo": self.yahoo.connect(),

            "kis": self.kis.connect(),

            "news": self.news.connect(),

            "dart": self.dart.connect(),

            "sec": self.sec.connect(),

            "fred": self.fred.connect()

        }


if __name__ == "__main__":

    adapters = AdapterManager().connect()

    print("=" * 60)
    print("ADAPTER MANAGER READY")
    print("=" * 60)

    for name, data in adapters.items():
        print(name, ":", data["status"])