import requests
from django.core.cache import cache

class CryptoPriceService:
    @staticmethod
    def fetch_market_data(symbol):
        """گرفتن قیمت و درصد تغییرات ۲۴ ساعته"""
        cache_key = f'market_data_{symbol.replace("/", "")}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data

        try:
            ticker = symbol.replace('/', '')
            url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={ticker}"
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                data = response.json()
                result = {
                    'price': float(data['lastPrice']),
                    'change': float(data['priceChangePercent'])
                }
                cache.set(cache_key, result, 30)
                return result
        except:
            pass
        return {'price': 0, 'change': 0}