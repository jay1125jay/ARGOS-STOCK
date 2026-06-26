from engines.stock.providers.kr_market_provider import KRMarketProvider
from engines.stock.providers.us_market_provider import USMarketProvider
from engines.stock.providers.news_provider import NewsProvider
from engines.stock.providers.dart_provider import DARTProvider
from engines.stock.providers.sec_provider import SECProvider


class ProviderManager:

    def __init__(self):

        self.kr = KRMarketProvider()

        self.us = USMarketProvider()

        self.news = NewsProvider()

        self.dart = DARTProvider()

        self.sec = SECProvider()

    def collect(self):

        return {

            "kr_market": self.kr.get(),

            "us_market": self.us.get(),

            "news": self.news.get(),

            "dart": self.dart.get(),

            "sec": self.sec.get()

        }


if __name__ == "__main__":

    manager = ProviderManager()

    data = manager.collect()

    print("=" * 60)

    print("PROVIDER MANAGER READY")

    print("=" * 60)

    for k in data:

        print(k, ":", data[k]["status"])