from django.shortcuts import render
from .models import LeadTrader, TradingPair
from services.price_fetcher import CryptoPriceService

def copy_trading_dashboard(request):
    # دریافت لیست تریدرها
    traders = LeadTrader.objects.all()
    
    # دریافت و آپدیت قیمت‌های ۵۰ ارز برتر (نمونه)
    pairs = TradingPair.objects.filter(is_active=True)
    for pair in pairs:
        current_real_price = CryptoPriceService.fetch_real_time_price(pair.symbol)
        if current_real_price > 0:
            pair.real_price = current_real_price
            pair.save()

    context = {
        'traders': traders,
        'pairs': pairs,
        'page_title': 'Copy Trading Dashboard'
    }
    return render(request, 'trading/copy_trading.html', context)