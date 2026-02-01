from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import DepositForm, WithdrawForm
from .models import Transaction

@login_required
def deposit_view(request):
    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            deposit = form.save(commit=False)
            deposit.user = request.user
            deposit.tx_type = 'deposit'
            deposit.status = 'pending'
            deposit.save()
            messages.success(request, "Deposit request submitted! Waiting for admin approval.") # اصلاح شد
            return redirect('transactions:history')
    else:
        form = DepositForm()
    
    return render(request, 'transactions/deposit.html', {
        'form': form,
        'wallet_address': "TYourAdminWalletAddressXYZ",
        'page_title': 'Deposit Funds' # اضافه شد
    })

@login_required
def withdraw_view(request):
    if request.method == 'POST':
        form = WithdrawForm(request.POST, user=request.user)
        if form.is_valid():
            withdraw = form.save(commit=False)
            withdraw.user = request.user
            withdraw.tx_type = 'withdraw'
            withdraw.status = 'pending'
            
            # Lock balance
            request.user.balance -= withdraw.amount
            request.user.save()
            
            withdraw.save()
            messages.success(request, "Withdrawal request submitted. Funds are locked until approval.") # اصلاح شد
            return redirect('transactions:history')
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