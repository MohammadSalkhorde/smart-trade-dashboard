import requests

class PriceService:
    @staticmethod
    def get_binance_price(symbol):
        """گرفتن قیمت واقعی از بایننس"""
        try:
            # تبدیل نماد به فرمت بایننس (مثلا BTC/USDT -> BTCUSDT)
            clean_symbol = symbol.replace('/', '')
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={clean_symbol}"
            response = requests.get(url, timeout=5)
            data = response.json()
            return float(data['price'])
        except Exception as e:
            print(f"Error fetching price for {symbol}: {e}")
            return 0.0