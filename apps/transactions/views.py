from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction as db_transaction
from .forms import DepositForm, WithdrawForm
from .models import Transaction
from apps.trading.models import SystemSettings
from apps.accounts.models import User

# ==================== DEPOSIT VIEW (MANUAL) ====================
@login_required
def deposit_view(request):
    # دریافت آدرس کیف پول‌های مدیریت از تنظیمات کلان سایت برای نمایش در فرانت‌اند
    settings_obj = SystemSettings.objects.first()
    wallet_trc20 = settings_obj.tron_wallet_address if settings_obj else "T..."
    wallet_bep20 = settings_obj.bsc_wallet_address if settings_obj else "0x..."

    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            deposit = form.save(commit=False)
            deposit.user = request.user
            deposit.tx_type = 'deposit'
            deposit.status = 'pending'  # به صورت پیش‌فرض در حال بررسی برای ادمین
            deposit.save()
            
            messages.success(
                request, 
                "Your deposit request has been submitted successfully. It will be credited after admin verification."
            )
            return redirect('transactions:history')
        else:
            messages.error(request, "Please fix the errors in the form.")
    else:
        form = DepositForm()
    
    return render(request, 'transactions/deposit.html', {
        'form': form,
        'wallet_trc20': wallet_trc20,
        'wallet_bep20': wallet_bep20,
        'page_title': 'Deposit Funds (USDT)'
    })


# ==================== WITHDRAW VIEW (MANUAL & SECURE) ====================
@login_required
def withdraw_view(request):
    if request.method == 'POST':
        form = WithdrawForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                # قفل کردن رکورد کاربر در دیتابیس برای جلوگیری از درخواست‌های همزمان (Race Condition)
                with db_transaction.atomic():
                    user = User.objects.select_for_update().get(id=request.user.id)
                    amount = form.cleaned_data.get('amount')
                    network = form.cleaned_data.get('network')
                    address = form.cleaned_data.get('tx_hash')
                    fee = Decimal('3.00')

                    # بررسی مجدد موجودی زیر چتر اتمیک دیتابیس
                    if user.balance < amount:
                        messages.error(request, f"Insufficient balance! Your current balance is ${user.balance}")
                        return render(request, 'transactions/withdraw.html', {'form': form})

                    # کسر موجودی بلافاصله بعد از درخواست (تا نتواند همزمان درخواست دیگری ثبت کند)
                    user.balance -= amount
                    user.save()
                    
                    # ثبت تراکنش پندینگ جهت تایید نهایی ادمین
                    withdraw = form.save(commit=False)
                    withdraw.user = user
                    withdraw.tx_type = 'withdraw'
                    withdraw.status = 'pending'
                    withdraw.network = network
                    withdraw.fee = fee
                    withdraw.tx_hash = address  # ذخیره آدرس ولت کاربر در فیلد هش
                    withdraw.save()

                    messages.success(request, "Withdrawal request submitted successfully.")
                    return redirect('transactions:history')

            except Exception as e:
                messages.error(request, "An internal error occurred. Please try again.")
                print(f"Withdraw Error: {e}")
        else:
            messages.error(request, "Please check the form for errors.")
    else:
        form = WithdrawForm(user=request.user)
    
    return render(request, 'transactions/withdraw.html', {
        'form': form,
        'page_title': 'Withdraw Funds'
    })


# ==================== TRANSACTION HISTORY ====================
@login_required
def transaction_history(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'transactions/history.html', {
        'transactions': transactions,
        'page_title': 'Transaction History'
    })


@login_required
def transaction_detail(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    return render(request, 'transactions/transaction_detail.html', {'tx': transaction})