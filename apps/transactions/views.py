from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import DepositForm, WithdrawForm
from .models import Transaction
from django.conf import settings
from .models import Transaction
from apps.trading.models import SystemSettings

from apps.accounts.tron_service import TronWalletService

# @login_required
# def deposit_view(request):
#     wallet_service = TronWalletService()
    
#     try:
#         user_wallet, created = wallet_service.get_or_create_user_wallet(request.user)
#     except Exception as e:
#         from django.contrib import messages
#         messages.error(request, f"Wallet system not ready. Please contact support. Error: {str(e)}")
#         return redirect('transactions:history')

#     if request.method == 'POST':
#         form = DepositForm(request.POST)
#         if form.is_valid():
#             deposit = form.save(commit=False)
#             deposit.user = request.user
#             deposit.tx_type = 'deposit'
#             deposit.status = 'pending'
#             deposit.network = 'TRC20'
#             deposit.tx_hash = ''
#             deposit.save()
            
#             from django.contrib import messages
#             messages.success(
#                 request, 
#                 f"Send exactly ${deposit.amount} USDT (TRC20) to your personal address: {user_wallet.address}"
#             )
#             return redirect('transactions:history')
#         else:
#             from django.contrib import messages
#             messages.error(request, "Please correct the errors below.")
#     else:
#         form = DepositForm()

#     return render(request, 'transactions/deposit.html', {
#         'form': form,
#         'user_wallet_address': user_wallet.address,
#         'page_title': 'Deposit USDT'
#     })
    
    
from apps.trading.models import SystemSettings
from django.conf import settings

@login_required
def deposit_view(request):
    pending_count = Transaction.objects.filter(user=request.user, status='pending', tx_type='deposit').count()
    if pending_count >= 3:
        messages.error(request, "You have too many pending requests. Please wait for admin approval.")
        return redirect('transactions:history')

    system_settings = SystemSettings.objects.first()
    
    if system_settings:
        wallet_trc20 = system_settings.tron_wallet_address
    else:
        wallet_trc20 = getattr(settings, 'TRON_WALLET_ADDRESS', "TBy5YFjUKjmCwLzdt3YoqjBpf493qVNrim")

    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            deposit = form.save(commit=False)
            deposit.user = request.user
            deposit.tx_type = 'deposit'
            deposit.status = 'pending'
            deposit.network = 'TRC20'
            deposit.save()
            messages.success(request, "Deposit request submitted successfully!")
            return redirect('transactions:history')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DepositForm()
    
    return render(request, 'transactions/deposit.html', {
        'form': form,
        'wallet_trc20': wallet_trc20,
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