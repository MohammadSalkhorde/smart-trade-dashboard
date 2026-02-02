from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.transactions.models import Transaction
from apps.trading.models import LeadTrader
from apps.trading.models import *

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_verified = True 
            user.save()
            
            login(request, user)
            messages.success(request, "Registration successful! Your account is now verified.")
            return redirect('trading:copy_list')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('trading:copy_list')
        else:
            # نمایش پیام خطا در صورت اشتباه بودن ایمیل یا پسورد
            messages.error(request, "Invalid email or password. Please try again.")
    else:
        form = AuthenticationForm()
        form.fields['username'].label = "Email"
        form.fields['username'].widget.attrs.update({'placeholder': 'Enter your email'})
    
    return render(request, 'accounts/login.html', {'form': form})
def logout_view(request):
    logout(request)
    return redirect('accounts:login')

@login_required
def user_dashboard(request):
    # 1. Get traders followed by the user
    my_followed_traders = FollowedTrader.objects.filter(user=request.user).select_related('trader')
    
    # 2. Get recent transactions
    recent_transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    context = {
        'followed_traders': my_followed_traders,
        'recent_transactions': recent_transactions,
        'page_title': 'User Dashboard'
    }
    return render(request, 'accounts/dashboard.html', context)

from django.db.models import Sum

@login_required
def profile_dashboard(request):
    followed_traders = FollowedTrader.objects.filter(user=request.user).select_related('trader')
    
    # محاسبه مجموع PnL بر اساس ROI تریدرها
    # فرض می‌کنیم PnL مجموع درصدهای تریدرهای فعال کاربر است
    total_pnl_percent = sum(item.trader.roi_30d for item in followed_traders)
    
    # محاسبه سود دلاری (اختیاری): 
    # total_pnl_usd = sum((item.investment_amount * item.trader.roi_30d) / 100 for item in followed_traders)

    recent_transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    context = {
        'followed_traders': followed_traders,
        'total_pnl': total_pnl_percent, # فرستادن مقدار به تمپلیت
        'recent_transactions': recent_transactions,
    }
    return render(request, 'accounts/dashboard.html', context)