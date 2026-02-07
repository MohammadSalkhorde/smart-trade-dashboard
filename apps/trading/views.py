from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from services.price_fetcher import CryptoPriceService
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal, InvalidOperation
from django.db import transaction 
from django.db.models import Q 
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt # برای اینکه در ارسال درخواست AJAX به مشکل نخورید
@login_required
def update_pnl_ajax(request):
    """ذخیره خودکار سود/ضرر هر 5 ثانیه"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            follow_id = data.get('id')
            pnl_value = data.get('pnl')
            
            # پیدا کردن پوزیشن کپی‌تریدینگ
            item = FollowedTrader.objects.filter(id=follow_id, user=request.user).first()
            if item:
                # ذخیره مقدار سود/ضرر لایو در دیتابیس
                item.last_pnl = Decimal(str(pnl_value))
                item.save()
                return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
    return JsonResponse({'status': 'fail'}, status=400)

@login_required
def copy_action(request, trader_id):
    """شروع کپی کردن یک تریدر"""
    trader = get_object_or_404(LeadTrader, id=trader_id)
    user = request.user
    
    if request.method == 'POST':
        amount_str = request.POST.get('amount')
        try:
            copy_amount = Decimal(amount_str)
        except (TypeError, ValueError, InvalidOperation):
            messages.error(request, "Invalid amount entered.")
            return redirect('trading:copy_list')

        if copy_amount < Decimal('1.00'):
            messages.error(request, "Minimum investment amount is $1.00")
            return redirect('trading:copy_list')

        if user.balance < copy_amount:
            messages.error(request, f"Insufficient balance! You need ${copy_amount}.")
            return redirect('transactions:deposit')

        with transaction.atomic():
            # تعیین سمبل ارز (BTC, ETH, etc) بر اساس ایندکس تریدر
            traders_list = list(LeadTrader.objects.all().order_by('id'))
            try:
                index = traders_list.index(trader) + 1
                if index % 5 == 0: symbol = "ADAUSDT"
                elif index % 4 == 0: symbol = "BNBUSDT"
                elif index % 3 == 0: symbol = "SOLUSDT"
                elif index % 2 == 0: symbol = "ETHUSDT"
                else: symbol = "BTCUSDT"
            except:
                symbol = "BTCUSDT"

            # گرفتن قیمت واقعی لحظه ورود از سرویس قیمت
            current_data = CryptoPriceService.fetch_market_data(symbol)
            current_entry_price = Decimal(str(current_data.get('price', 0)))

            # کسر از موجودی کاربر
            user.balance -= copy_amount
            user.save()
            
            # اضافه کردن به AUM تریدر
            trader.aum = Decimal(trader.aum) + copy_amount
            trader.save()
            
            # ایجاد یا آپدیت رکورد فالو
            follow, created = FollowedTrader.objects.get_or_create(
                user=user, 
                trader=trader,
                defaults={
                    'investment_amount': copy_amount,
                    'entry_price': current_entry_price,
                    'last_pnl': 0
                }
            )
            
            if not created:
                # اگر از قبل کپی می‌کرده، مبلغ جدید اضافه شود و قیمت ورود جدید فیکس شود
                follow.investment_amount += copy_amount
                follow.entry_price = current_entry_price
                follow.save()

        messages.success(request, f"Successfully started copying {trader.name} with ${copy_amount}!")
        return redirect('accounts:dashboard')
    
    return redirect('trading:copy_list')

@login_required
def stop_copy_action(request, follow_id):
    """توقف کپی و بازگشت سرمایه + سود/ضرر به موجودی"""
    followed_trader = get_object_or_404(FollowedTrader, id=follow_id, user=request.user)
    
    if request.method == 'POST':
        live_pnl_str = request.POST.get('live_pnl', '0')
        try:
            percent_change = Decimal(live_pnl_str)
        except (InvalidOperation, TypeError):
            percent_change = Decimal('0')

        with transaction.atomic():
            user = request.user
            trader = followed_trader.trader
            initial_amount = followed_trader.investment_amount
            
            # محاسبه سود یا ضرر نهایی
            profit_loss = initial_amount * (percent_change / Decimal('100'))
            final_return_amount = initial_amount + profit_loss

            # بازگشت پول به کیف پول کاربر
            user.balance = Decimal(user.balance) + final_return_amount
            user.save()
            
            # کسر از AUM تریدر
            trader.aum = max(Decimal('0'), Decimal(trader.aum) - initial_amount)
            trader.save()
            
            trader_name = trader.name
            followed_trader.delete() 
            
            messages.success(
                request, 
                f"Stopped copying {trader_name}. Final amount of ${final_return_amount:.2f} "
                f"({percent_change}% PnL) returned to your balance."
            )
    
    return redirect('accounts:dashboard')

# --- توابع کمکی دیگر (بدون تغییرات خاص) ---

def copy_trading_dashboard(request):
    query = request.GET.get('q') 
    traders = LeadTrader.objects.filter(Q(name__icontains=query) | Q(aum__icontains=query)) if query else LeadTrader.objects.all()
    pairs = TradingPair.objects.filter(is_active=True)
    
    for pair in pairs:
        try:
            current_real_price = CryptoPriceService.fetch_real_time_price(pair.symbol, pair.real_price)
            if current_real_price > 0:
                pair.real_price = current_real_price
                pair.save()
        except: pass 

    return render(request, 'trading/copy_trading.html', {'traders': traders, 'pairs': pairs, 'page_title': 'Copy Trading'})

def market_list(request):
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

def trader_detail(request, trader_id):
    trader = get_object_or_404(LeadTrader, id=trader_id)
    return render(request, 'trading/trader_detail.html', {'trader': trader})