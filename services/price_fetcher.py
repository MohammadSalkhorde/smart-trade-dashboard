import requests

class CryptoPriceService:
    @staticmethod
    def fetch_real_time_price(symbol, current_price=None):
        """دریافت قیمت واقعی با مکانیزم Fallback"""
        try:
            ticker = symbol.replace('/', '')
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={ticker}"
            
            # تایم‌اوت رو به 10 ثانیه افزایش دادیم
            response = requests.get(url, timeout=10) 
            
            if response.status_code == 200:
                return float(response.json()['price'])
        
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
        
        # نکته طلایی: اگر خطا خورد، قیمت قبلی رو برگردون نه صفر!
        return current_price if current_price is not None else 0.0