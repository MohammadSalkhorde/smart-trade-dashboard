from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import DepositForm, WithdrawForm
from .models import Transaction
from django.conf import settings
from .models import Transaction
from apps.trading.models import SystemSettings

@login_required
def deposit_view(request):
    # جلوگیری از ثبت بیش از ۳ درخواست در جریان
    pending_count = Transaction.objects.filter(user=request.user, status='pending', tx_type='deposit').count()
    if pending_count >= 3:
        messages.error(request, "You have too many pending requests. Please wait for admin approval.")
        return redirect('transactions:history')

    # دریافت تنظیمات سیستم برای نمایش آدرس کیف پول‌ها
    system_settings = SystemSettings.objects.first()
    
    # مدیریت آدرس‌ها (TRC20 و BEP20) برای نمایش در تمپلیت
    if system_settings:
        wallet_trc20 = system_settings.tron_wallet_address
        wallet_bep20 = getattr(system_settings, 'bsc_wallet_address', "0xAddressNotSet")
    else:
        wallet_trc20 = getattr(settings, 'TRON_WALLET_ADDRESS', "TBy5YFjUKjmCwLzdt3YoqjBpf493qVNrim")
        wallet_bep20 = getattr(settings, 'BSC_WALLET_ADDRESS', "0xDefaultAddress")

    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            deposit = form.save(commit=False)
            deposit.user = request.user
            deposit.tx_type = 'deposit'
            deposit.status = 'pending'
            # فیلد network به طور خودکار از form.cleaned_data برداشته شده و ذخیره می‌شود
            deposit.save()
            messages.success(request, "Deposit request submitted successfully!")
            return redirect('transactions:history')
        else:
            # اگر فرم خطا داشت (مثل همون خطای فیلد اجباری)، پیغام بده
            messages.error(request, "Please correct the errors below.")
    else:
        form = DepositForm()
    
    return render(request, 'transactions/deposit.html', {
        'form': form,
        'wallet_trc20': wallet_trc20,
        'wallet_bep20': wallet_bep20,
        'page_title': 'Deposit USDT'
    })


from decimal import Decimal

@login_required
def withdraw_view(request):
    if request.method == 'POST':
        form = WithdrawForm(request.POST, user=request.user)
        if form.is_valid():
            withdraw = form.save(commit=False)
            
            network = form.cleaned_data.get('network')
            amount = form.cleaned_data.get('amount')
            fee = Decimal('3.00')

            if request.user.balance < amount:
                messages.error(request, f"Insufficient balance! Your current balance is ${request.user.balance}")
                return render(request, 'transactions/withdraw.html', {'form': form})

            withdraw.user = request.user
            withdraw.tx_type = 'withdraw'
            withdraw.status = 'pending'
            withdraw.network = network
            withdraw.fee = fee
            
            request.user.balance -= amount
            request.user.save()
            
            withdraw.save()
            messages.success(request, "Withdrawal request submitted successfully.")
            return redirect('transactions:history')
        else:
            messages.error(request, "Please check the form for errors.")
    else:
        form = WithdrawForm(user=request.user)
    
    return render(request, 'transactions/withdraw.html', {
        'form': form,
        'page_title': 'Withdraw Funds'
    })
    
@login_required
def transaction_history(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'transactions/history.html', {
        'transactions': transactions,
        'page_title': 'Transaction History'
    })
    

def transaction_detail(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    return render(request, 'transactions/transaction_detail.html', {'tx': transaction})