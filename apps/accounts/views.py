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
    # ۱. بررسی وجود کد معرف در URL و ذخیره در سشن (Session)
    # این باعث می‌شود حتی اگر کاربر بعد از کلیک روی لینک، چند صفحه دیگر را ببیند و بعد ثبت‌نام کند، کد گم نشود.
    ref_code_from_url = request.GET.get('ref')
    if ref_code_from_url:
        request.session['referrer_code'] = ref_code_from_url

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # ایجاد شیء کاربر بدون ذخیره نهایی در دیتابیس
            user = form.save(commit=False)
            user.is_verified = True  # تایید خودکار اکانت
            
            # ۲. بررسی سشن برای پیدا کردن معرف و اتصال به کاربر جدید
            ref_code = request.session.get('referrer_code')
            if ref_code:
                try:
                    referrer = User.objects.get(referral_code=ref_code)
                    user.referred_by = referrer
                    
                    # ۳. ایجاد یک اعلان دائمی برای شخص معرف
                    # این پیام در دیتابیس می‌ماند تا معرف هر زمان وارد شد آن را ببیند
                    Notification.objects.create(
                        user=referrer,
                        message=f"Success! A new user ({user.username}) joined using your referral link."
                    )
                    
                    # یک پیام خوش‌آمدگویی برای خود کاربر جدید
                    messages.info(request, f"You have been referred by {referrer.username}.")
                
                except User.DoesNotExist:
                    # اگر کد معرف نامعتبر بود، اتفاقی نمی‌افتد و ثبت‌نام عادی انجام می‌شود
                    pass
            
            # ذخیره نهایی کاربر در دیتابیس
            user.save()
            
            # پاک کردن کد معرف از سشن بعد از ثبت‌نام موفق
            if 'referrer_code' in request.session:
                del request.session['referrer_code']

            # ۴. ورود خودکار کاربر و هدایت به پنل
            login(request, user)
            messages.success(request, "Your account has been created successfully!")
            return redirect('trading:copy_list')
        else:
            # نمایش خطاهای فرم (مثل تکراری بودن ایمیل و ...)
            messages.error(request, "Registration failed. Please check the errors below.")
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
            messages.error(request, "Invalid email or password.")
    else:
        form = AuthenticationForm()
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
            # ریدایرکت به همین صفحه برای دیدن تغییرات و پیام موفقیت
            return redirect('accounts:profile_dashboard') 
    else:
        form = UserProfileForm(instance=request.user)

    my_followed_traders = FollowedTrader.objects.filter(user=request.user).select_related('trader')
    recent_transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')[:5]
    my_referrals = User.objects.filter(referred_by=request.user)

    context = {
        'form': form,
        'followed_traders': my_followed_traders,
        'recent_transactions': recent_transactions,
        'my_referrals': my_referrals,
        'referral_link': f"{request.build_absolute_uri('/accounts/register/')}?ref={request.user.referral_code}",
        'page_title': 'Account Settings'
    }
    return render(request, 'users/profile.html', context)

@login_required
def profile_dashboard(request):
    # --- بخش جدید: خوانده شده علامت زدن نوتیفیکیشن‌ها به محض ورود به داشبورد اصلی ---
    request.user.notifications.filter(is_read=False).update(is_read=True)    # -----------------------------------------------------------------------

    followed_traders = FollowedTrader.objects.filter(user=request.user).select_related('trader')
    
    # جلوگیری از خطا اگر مقدار roi_30d نال بود
    total_pnl_percent = sum((item.trader.roi_30d or 0) for item in followed_traders)
    
    recent_transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    context = {
        'followed_traders': followed_traders,
        'total_pnl': total_pnl_percent,
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