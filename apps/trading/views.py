from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from services.price_fetcher import CryptoPriceService
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
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
    user = request.user
    
    # تعیین یک مبلغ ثابت برای کپی کردن (مثلاً ۱۰۰ دلار) یا می‌توانید از فرم بگیرید
    copy_amount = Decimal('100.00') 

    # ۱. چک کردن موجودی کاربر
    if user.balance < copy_amount:
        messages.error(request, f"Insufficient balance! You need at least ${copy_amount} to copy this trader.")
        return redirect('trading:copy_list')

    # ۲. چک کردن اینکه آیا قبلاً این تریدر را کپی کرده یا خیر
    already_following = FollowedTrader.objects.filter(user=user, trader=trader).exists()
    if already_following:
        messages.warning(request, "You are already following this trader.")
        return redirect('accounts:dashboard')

    # ۳. کسر مبلغ از موجودی کاربر و ذخیره
    user.balance -= copy_amount
    user.save()

    # ۴. ثبت در جدول تریدرهای کپی شده
    FollowedTrader.objects.create(
        user=user, 
        trader=trader, 
        investment_amount=copy_amount
    )

    messages.success(request, f"Strategy copying started! ${copy_amount} has been allocated to {trader.name}.")
    return redirect('accounts:dashboard')

@login_required
def stop_copy_action(request, follow_id):
    # پیدا کردن رکورد کپی بر اساس ID
    followed_trader = get_object_or_404(FollowedTrader, id=follow_id, user=request.user)
    
    # برگرداندن پول به موجودی کاربر
    user = request.user
    user.balance += followed_trader.investment_amount
    user.save()
    
    # حذف رکورد از لیست کپی‌ها
    trader_name = followed_trader.trader.name
    followed_trader.delete()
    
    messages.info(request, f"Stopped copying {trader_name}. Funds have been returned to your balance.")
    return redirect('accounts:dashboard')


def trader_detail(request, trader_id):
    """نمایش صفحه جزئیات هر تریدر (پروفایل)"""
    trader = get_object_or_404(LeadTrader, id=trader_id)
    # اینجا می‌توانید آمارهای دقیق‌تر یا لیست اوردرها را هم بگیرید
    context = {
        'trader': trader,
        'page_title': f"{trader.name}'s Profile"
    }
    return render(request, 'trading/trader_detail.html', context)