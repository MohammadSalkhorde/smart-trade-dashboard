from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from services.price_fetcher import CryptoPriceService
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
from django.db import transaction 

def copy_trading_dashboard(request):
    """نمایش لیست تریدرها و آپدیت قیمت‌ها"""
    traders = LeadTrader.objects.all()
    pairs = TradingPair.objects.filter(is_active=True)
    
    for pair in pairs:
        try:
            # استفاده از قیمت لحظه‌ای با Fallback قیمت دیتابیس
            current_real_price = CryptoPriceService.fetch_real_time_price(pair.symbol, pair.real_price)
            if current_real_price > 0:
                pair.real_price = current_real_price
                pair.save()
        except Exception:
            pass 

    return render(request, 'trading/copy_trading.html', {
        'traders': traders,
        'pairs': pairs,
        'page_title': 'Copy Trading'
    })

def trader_detail(request, trader_id):
    """نمایش جزئیات تریدر"""
    trader = get_object_or_404(LeadTrader, id=trader_id)
    return render(request, 'trading/trader_detail.html', {
        'trader': trader,
        'open_orders': []  
    })

@login_required
def copy_action(request, trader_id):
    """عملیات کپی تریدینگ با چک کردن موجودی و هدایت به واریز"""
    trader = get_object_or_404(LeadTrader, id=trader_id)
    user = request.user
    
    # دریافت مبلغ از فرم (پیش‌فرض 100 دلار)
    amount_str = request.POST.get('amount', '100.00')
    try:
        copy_amount = Decimal(amount_str)
    except:
        copy_amount = Decimal('100.00')

    # کنترل موجودی: اگر کافی نبود، پیام بده و بفرست صفحه واریز
    if user.balance < copy_amount:
        messages.error(request, f"Insufficient balance! You need ${copy_amount}. Please deposit first.")
        return redirect('transactions:deposit')

    with transaction.atomic():
        # کسر از موجودی کاربر
        user.balance -= copy_amount
        user.save()
        
        # آپدیت دارایی تحت مدیریت تریدر (AUM)
        trader.aum = Decimal(trader.aum) + copy_amount
        trader.save()
        
        # ایجاد یا آپدیت رکورد کپی
        follow, created = FollowedTrader.objects.get_or_create(
            user=user, 
            trader=trader,
            defaults={'investment_amount': copy_amount}
        )
        
        if not created:
            follow.investment_amount += copy_amount
            follow.save()

    messages.success(request, f"Successfully started copying {trader.name} with ${copy_amount}!")
    # هدایت به داشبورد (نام صحیح در urls شما 'dashboard' است)
    return redirect('accounts:dashboard')

@login_required
def stop_copy_action(request, follow_id):
    """توقف کپی و بازگشت وجه به کیف پول کاربر"""
    followed_trader = get_object_or_404(FollowedTrader, id=follow_id, user=request.user)
    
    with transaction.atomic():
        user = request.user
        # بازگشت وجه
        user.balance += followed_trader.investment_amount
        user.save()
        
        # کم کردن از AUM تریدر
        trader = followed_trader.trader
        trader.aum = max(0, Decimal(trader.aum) - followed_trader.investment_amount)
        trader.save()
        
        trader_name = trader.name
        followed_trader.delete()
    
    messages.info(request, f"Stopped copying {trader_name}. Funds returned to your balance.")
    return redirect('accounts:dashboard')

def market_list(request):
    """نمایش لیست مارکت"""
    pairs = TradingPair.objects.filter(is_active=True)
    market_data = [] 
    for pair in pairs:
        data = CryptoPriceService.fetch_market_data(pair.symbol)
        market_data.append({
            'name': pair.display_name,
            'symbol': pair.symbol,
            'display_price': data['price'] if data['price'] > 0 else pair.real_price,
            'manipulation': data['change'] if data['change'] != 0 else pair.manipulation_percent
        })
        
    return render(request, 'trading/market.html', {'market_data': market_data})