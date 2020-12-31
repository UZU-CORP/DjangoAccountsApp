from typing import Any
import requests

class CoinRateRetriever:
    PRICE_URL = "https://api.coindesk.com/v1/bpi/currentprice.json"
    
    __timeout: int
    __cache: Any

    def __init__(self, cache=None, timeoutSeconds=10):
        self.__timeout = timeoutSeconds * 1000
        self.__cache = cache

    def __get_from_cache(self, key):
        if not self.__cache:
            return None
        return self.__cache.get(key, None)

    def __store_in_cache(self, key, value):
        if not self.__cache:
            return
        self.__cache.add(key, value, self.__timeout)

    def get_btc_price(self, currency="USD"):
        cache_price = self.__get_from_cache(currency)
        if cache_price:
            return cache_price
        response = requests.get(self.__class__.PRICE_URL)
        try:
            response_data = response.json()
            price = response_data["bpi"][currency]["rate_float"]
            self.__store_in_cache(currency, price)
            return price
        except Exception:
            return None
