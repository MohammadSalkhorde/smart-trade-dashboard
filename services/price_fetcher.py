import requests

class CryptoPriceService:
    @staticmethod
    def fetch_real_time_price(symbol):
        """دریافت قیمت واقعی از API بایننس"""
        try:
            # حذف اسلش برای هماهنگی با API
            ticker = symbol.replace('/', '')
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={ticker}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return float(response.json()['price'])
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
        return 0.0