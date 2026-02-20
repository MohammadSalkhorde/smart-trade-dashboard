from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.transactions.models import Transaction
from apps.trading.models import LeadTrader, FollowedTrader
from django.contrib.auth import get_user_model
from .models import *

User = get_user_model()

def register_view(request):
    
    if request.user.is_authenticated:
        return redirect('trading:copy_list')
    
    ref_code_from_url = request.GET.get('ref')
    if ref_code_from_url:
        request.session['referrer_code'] = ref_code_from_url

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            
            user.username = form.cleaned_data.get('email')
            user.is_verified = True  
            
            ref_code = request.session.get('referrer_code')
            if ref_code:
                try:
                    referrer = User.objects.get(referral_code=ref_code)
                    user.referred_by = referrer
                    

                except User.DoesNotExist:
                    pass
            
            user.save()

            if user.referred_by:
                Notification.objects.create(
                    user=user.referred_by,
                    message=f"Success! A new user ({user.email}) joined using your referral link."
                )
                messages.info(request, f"You have been referred by {user.referred_by.username}.")

            if 'referrer_code' in request.session:
                del request.session['referrer_code']

            login(request, user)
            messages.success(request, "Your account has been created successfully!")
            return redirect('trading:copy_list')
        else:
            messages.error(request, "Registration failed. Please check the errors below.")
    else:
        form = RegisterForm()
    
    return render(request, 'accounts/register.html', {'form': form})
    
from django.views.decorators.csrf import csrf_exempt 

# @csrf_exempt
def login_view(request):
    if request.user.is_authenticated:
        return redirect('trading:copy_list') 

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            request.session.modified = True
            request.session.save() 
            
            messages.success(request, f"Welcome back!")
            return redirect('trading:copy_list')
        else:
            messages.error(request, "Invalid email or password.")
    else:
        form = AuthenticationForm()
        if 'username' in form.fields:
            form.fields['username'].label = "Email"
            
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('accounts:login')


@login_required
def user_dashboard(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect(request.path) 
    else:
        form = UserProfileForm(instance=request.user)

    referral_earnings = request.user.referral_earnings 
    my_referrals = User.objects.filter(referred_by=request.user)
    referral_link = f"{request.build_absolute_uri('/accounts/register/')}?ref={request.user.referral_code}"

    context = {
        'form': form,
        'my_referrals': my_referrals,
        'referral_count': my_referrals.count(),
        'referral_earnings': referral_earnings, 
        'referral_link': referral_link,
        'page_title': 'Account Settings'
    }
    return render(request, 'users/profile.html', context)


@login_required
def profile_dashboard(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)

    followed_traders = FollowedTrader.objects.filter(user=request.user).select_related('trader')
    
    total_positions = followed_traders.count()
    if total_positions > 0:
        total_pnl_percent = sum((item.trader.roi_30d or 0) for item in followed_traders) / total_positions
    else:
        total_pnl_percent = 0
    
    recent_transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    context = {
        'followed_traders': followed_traders,
        'total_pnl': round(total_pnl_percent, 2),
        'recent_transactions': recent_transactions,
    }
    return render(request, 'accounts/dashboard.html', context)


def user_notifications(request):

    if request.user.is_authenticated:
        return {
            'unread_notifications': request.user.notifications.filter(is_read=False).order_by('-created_at')
        }
    return {}


from django.http import JsonResponse

@login_required
def mark_notification_as_read(request, pk):
    if request.method == 'POST':
        notification = request.user.notifications.filter(pk=pk).first()
        if notification:
            notification.is_read = True
            notification.save()
            return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)


