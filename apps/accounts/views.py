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
    # 1. Get traders followed by the user
    my_followed_traders = FollowedTrader.objects.filter(user=request.user).select_related('trader')
    
    # 2. Get recent transactions
    recent_transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    context = {
        'followed_traders': my_followed_traders,
        'recent_transactions': recent_transactions,
        'page_title': 'User Dashboard' # اصلاح شد
    }
    return render(request, 'accounts/dashboard.html', context)



@login_required
def profile_dashboard(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('accounts:profile_dashboard')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'users/profile.html', {'form': form})