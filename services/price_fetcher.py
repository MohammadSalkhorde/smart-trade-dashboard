import requests

def get_live_price(symbol):
    """گرفتن قیمت لحظه‌ای از یک API رایگان مثل Binance یا CoinGecko"""
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT"
        response = requests.get(url).json()
        return float(response['price'])
    except:
        return 0.0