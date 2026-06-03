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
from apps.accounts.models import User
from apps.accounts.decorators import block_banned_users

@csrf_exempt 
@login_required
def update_pnl_ajax(request):
    """ذخیره خودکار سود/ضرر نهایی کاربر (محاسبه شده در کلاینت)"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            follow_id = data.get('id')
            pnl_value = data.get('pnl') 
            
            item = FollowedTrader.objects.filter(id=follow_id, user=request.user).first()
            if item:
                item.last_pnl = Decimal(str(pnl_value))
                item.save()
                return JsonResponse({'status': 'success'})
            return JsonResponse({'status': 'error', 'message': 'Position not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'fail'}, status=400)


@block_banned_users
@login_required
def copy_action(request, trader_id):
    """شروع کپی یا افزایش موجودی با حفظ دقیق درصد سود (PnL%) قبلی"""
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
            messages.error(request, f"Insufficient balance!")
            return redirect('transactions:deposit')

        try:
            with transaction.atomic():
                # ۱. دریافت دیتای سمبل و ROI فعلی
                try:
                    traders_list = list(LeadTrader.objects.all().order_by('id'))
                    index = traders_list.index(trader) + 1
                    symbols = {0:"ADAUSDT", 4:"BNBUSDT", 3:"SOLUSDT", 2:"ETHUSDT"}
                    symbol = symbols.get(index % 5, "BTCUSDT")
                except:
                    symbol = "BTCUSDT"

                current_trader_roi = trader.roi_30d 

                # ۲. کسر از موجودی کاربر و آپدیت AUM
                user.balance -= copy_amount
                user.save()
                
                trader.aum = Decimal(trader.aum) + copy_amount
                trader.save()
                
                # ۳. مدیریت پوزیشن کپی
                follow = FollowedTrader.objects.filter(user=user, trader=trader, is_active=True).first()
                
                if follow:
                    # --- منطق حفظ درصد سود (PnL Persistence) ---
                    
                    # الف) محاسبه درصد سود فعلی پوزیشن
                    current_pnl_percent = current_trader_roi - follow.entry_roi
                    
                    # ب) محاسبه ضریب تعدیل
                    # اگر سود ۱۰۰٪ باشد، ضریب می‌شود ۲ (۱ + ۱۰۰/۱۰۰)
                    # اگر ضرر ۲۰٪ باشد، ضریب می‌شود ۰.۸ (۱ - ۲۰/۱۰۰)
                    adjustment_factor = (Decimal('1') + (current_pnl_percent / Decimal('100')))
                    
                    # ج) تعدیل مبلغ واریزی جدید
                    # برای اینکه درصد تغییر نکند، مبلغ واریزی باید بر ضریب سود تقسیم شود
                    # این کار باعث می‌شود در محاسبات فرانت‌اِند، سود روی این مبلغ هم اعمال شود و عدد نهایی درست دربیاید
                    if adjustment_factor > 0:
                        adjusted_deposit = copy_amount / adjustment_factor
                        follow.investment_amount += adjusted_deposit
                    else:
                        # اگر پوزیشن در ضرر ۱۰۰٪ (لیکویید) باشد، عملاً ریست می‌شود
                        follow.investment_amount = copy_amount
                        follow.entry_roi = current_trader_roi

                    follow.save()
                    messages.success(request, f"Added ${copy_amount}. PnL% maintained.")
                else:
                    # ایجاد پوزیشن جدید
                    current_data = CryptoPriceService.fetch_market_data(symbol)
                    current_entry_price = Decimal(str(current_data.get('price', 0)))
                    
                    FollowedTrader.objects.create(
                        user=user, 
                        trader=trader,
                        investment_amount=copy_amount,
                        entry_price=current_entry_price,
                        entry_roi=current_trader_roi, 
                        last_pnl=0,
                        is_active=True
                    )
                    messages.success(request, f"Successfully started copying {trader.name}!")

            return redirect('accounts:dashboard')

        except Exception as e:
            print(f"Error in copy_action: {e}")
            messages.error(request, "Error processing request.")
            return redirect('trading:copy_list')
    
    return redirect('trading:copy_list')

@login_required
def stop_copy_action(request, follow_id):
    """توقف کپی و محاسبه بازگشت وجه بر اساس سود لحظه خروج با حفظ کف موجودی (صفر)"""
    
    # پیدا کردن پوزیشن کپی (اطمینان از اینکه متعلق به همین کاربر است)
    followed_trader = get_object_or_404(FollowedTrader, id=follow_id, user=request.user)
    
    if request.method == 'POST':
        live_pnl_str = request.POST.get('live_pnl', '0')
        try:
            percent_change = Decimal(live_pnl_str)
        except (InvalidOperation, TypeError):
            percent_change = Decimal('0')

        # ۱. جلوگیری از ضرر بیش از ۱۰۰ درصد (صفر شدن موجودی به جای منفی شدن)
        if percent_change < Decimal('-100'):
            percent_change = Decimal('-100')

        try:
            with transaction.atomic():
                # ۲. استفاده از select_for_update برای جلوگیری از ارور Database is Locked
                # این کار رکورد کاربر را در دیتابیس رزرو می‌کند تا محاسبات دقیق انجام شود
                user = User.objects.select_for_update().get(id=request.user.id)
                trader = followed_trader.trader
                initial_amount = followed_trader.investment_amount
                
                # ۳. محاسبه سود/ضرر و مبلغ نهایی برگشتی
                # فرمول: سرمایه اولیه + (سرمایه اولیه * درصد سود/ضرر)
                profit_loss = initial_amount * (percent_change / Decimal('100'))
                final_return_amount = initial_amount + profit_loss
                
                # اطمینان نهایی که مبلغ برگشتی هرگز زیر صفر نرود
                if final_return_amount < 0:
                    final_return_amount = Decimal('0.00')

                # ۴. آپدیت موجودی کاربر
                user.balance = Decimal(user.balance) + final_return_amount
                user.save()
                
                # ۵. کسر سرمایه از AUM تریدر
                trader.aum = max(Decimal('0'), Decimal(trader.aum) - initial_amount)
                trader.save()
                
                trader_name = trader.name
                
                # ۶. حذف پوزیشن کپی (یا می‌توانید is_active=False کنید)
                followed_trader.delete() 
                
                messages.success(
                    request, 
                    f"Stopped copying {trader_name}. Final amount of ${final_return_amount:.2f} "
                    f"({percent_change}% PnL) returned to your balance."
                )
        except Exception as e:
            # مدیریت خطاهای احتمالی دیتابیس
            print(f"Error in stop_copy_action: {e}")
            messages.error(request, "An error occurred while settling the trade. Please try again.")
            
    return redirect('accounts:dashboard')
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
    context = {
        'trader': trader,
        'is_admin': request.user.is_staff,
        'chart_data': trader.chart_history_json
    }
    return render(request, 'trading/trader_detail.html', context)

@login_required
def update_trader_chart(request, trader_id):
    """آپدیت چارت توسط ادمین و همگام‌سازی ROI تریدر"""
    if request.user.is_staff and request.method == 'POST':
        try:
            data = json.loads(request.body)
            trader = LeadTrader.objects.get(id=trader_id)
            points = data.get('points', [])
            
            # تبدیل نقاط به فرمت اعشاری برای دیتابیس
            cleaned_points = [float(p) for p in points]
            trader.chart_history_json = cleaned_points
            
            if cleaned_points:
                # آخرین نقطه نمودار به عنوان سود ۳۰ روزه تریدر در نظر گرفته می‌شود
                new_roi = Decimal(str(cleaned_points[-1]))
                
                # جلوگیری از فراتر رفتن از بازه تعیین شده در دیتابیس (اختیاری)
                if new_roi > 1000: new_roi = Decimal('1000.00')
                if new_roi < -100: new_roi = Decimal('-100.00')
                
                trader.roi_30d = new_roi
            
            trader.save()
            return JsonResponse({'status': 'ok', 'new_roi': float(trader.roi_30d)})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'forbidden'}, status=403)

@login_required
def get_latest_pnl(request, follow_id):
    """ارسال اطلاعات لحظه‌ای تریدر برای محاسبه در کلاینت"""
    try:
        item = get_object_or_404(FollowedTrader, id=follow_id, user=request.user)
        return JsonResponse({
            'trader_roi': float(item.trader.roi_30d), 
            'is_manual': getattr(item.trader, 'is_manual_mode', False),
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)