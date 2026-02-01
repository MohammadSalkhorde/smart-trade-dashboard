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
            # ارسال قیمت فعلی دیتابیس به عنوان Fallback برای جلوگیری از کندی
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
    """نمایش جزئیات تریدر بدون نیاز به مدل Order"""
    trader = get_object_or_404(LeadTrader, id=trader_id)
    
    # چون مدل Order نداریم، فعلاً لیست سفارشات باز را خالی می‌فرستیم
    # یا می‌توانیم از داده‌های استاتیک برای نمایش در ظاهر استفاده کنیم
    return render(request, 'trading/trader_detail.html', {
        'trader': trader,
        'open_orders': []  # لیست خالی برای جلوگیری از ارور در تمپلیت
    })

@login_required
def copy_action(request, trader_id):
    trader = get_object_or_404(LeadTrader, id=trader_id)
    user = request.user
    
    # مبلغ را از فرم بگیر، اگر نبود پیش‌فرض 100
    amount_str = request.POST.get('amount', '100.00')
    try:
        copy_amount = Decimal(amount_str)
    except:
        copy_amount = Decimal('100.00')

    if user.balance < copy_amount:
        messages.error(request, f"Insufficient balance! You need ${copy_amount}")
        return redirect('trading:copy_trading_dashboard')

    with transaction.atomic():
        # کسر از موجودی کاربر
        user.balance -= copy_amount
        user.save()
        
        # اضافه کردن به دارایی تحت مدیریت تریدر (برای کلاس کار!)
        trader.aum = Decimal(trader.aum) + copy_amount
        trader.save()
        
        FollowedTrader.objects.create(
            user=user, 
            trader=trader, 
            investment_amount=copy_amount
        )

    messages.success(request, f"Successfully started copying {trader.name} with ${copy_amount}!")
    return redirect('accounts:dashboard')

@login_required
def stop_copy_action(request, follow_id):
    """توقف کپی و بازگشت وجه"""
    followed_trader = get_object_or_404(FollowedTrader, id=follow_id, user=request.user)
    
    with transaction.atomic():
        user = request.user
        user.balance += followed_trader.investment_amount
        user.save()
        
        trader_name = followed_trader.trader.name
        followed_trader.delete()
    
    messages.info(request, f"Stopped copying {trader_name}. Funds returned to balance.")
    return redirect('accounts:dashboard')

def market_list(request):
    """نمایش لیست مارکت با قیمت‌های آپدیت شده"""
    pairs = TradingPair.objects.filter(is_active=True)
    
    market_data = [] # ساخت لیستی که تمپلیت منتظر آن است
    for pair in pairs:
        # استفاده از سرویس کش که قبلاً نوشتیم برای سرعت بالا
        data = CryptoPriceService.fetch_market_data(pair.symbol)
        
        market_data.append({
            'name': pair.display_name,
            'symbol': pair.symbol,
            'display_price': data['price'] if data['price'] > 0 else pair.real_price,
            'manipulation': data['change'] if data['change'] != 0 else pair.manipulation_percent
        })
        
    return render(request, 'trading/market.html', {'market_data': market_data})