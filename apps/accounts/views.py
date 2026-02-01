from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm 
from django.contrib.auth.decorators import login_required
from apps.transactions.models import Transaction
from apps.trading.models import LeadTrader

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
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
            return redirect('trading:copy_list')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('accounts:login')


@login_required
def user_dashboard(request):
    # تاریخچه تراکنش‌های اخیر کاربر
    recent_transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    # اینجا در آینده مدل 'FollowedTraders' رو اضافه می‌کنیم
    # فعلاً برای خالی نبودن، تریدرهای برتر رو نشون می‌دیم
    suggested_traders = LeadTrader.objects.all()[:3]

    context = {
        'recent_transactions': recent_transactions,
        'suggested_traders': suggested_traders,
        'page_title': 'Account Dashboard'
    }
    return render(request, 'accounts/dashboard.html', context)