from engines.stock.providers.kr_market_provider import KRMarketProvider
from engines.stock.providers.us_market_provider import USMarketProvider
from engines.stock.providers.news_provider import NewsProvider
from engines.stock.providers.dart_provider import DARTProvider
from engines.stock.providers.sec_provider import SECProvider

from engines.stock.providers.adapters.adapter_manager import AdapterManager
from engines.stock.providers.data_cache import DataCache


class ProviderManager:

    def __init__(self):

        self.kr = KRMarketProvider()
        self.us = USMarketProvider()
        self.news = NewsProvider()
        self.dart = DARTProvider()
        self.sec = SECProvider()

        self.adapters = AdapterManager()

        self.cache = DataCache()

    def collect(self):

        data = {

            "providers": {

                "kr_market": self.kr.get(),
                "us_market": self.us.get(),
                "news": self.news.get(),
                "dart": self.dart.get(),
                "sec": self.sec.get()

            },

            "adapters": self.adapters.connect()

        }

        self.cache.save(data)

        return data


if __name__ == "__main__":

    manager = ProviderManager()

    data = manager.collect()

    print("=" * 60)
    print("PROVIDER MANAGER READY")
    print("=" * 60)

    for k in data["providers"]:
        print(k, ":", data["providers"][k]["status"])

    for k in data["adapters"]:
        print(k, ":", data["adapters"][k]["status"])