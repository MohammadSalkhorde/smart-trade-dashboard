from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import DepositForm, WithdrawForm
from .models import Transaction
from django.conf import settings

@login_required
def deposit_view(request):

    pending_count = Transaction.objects.filter(user=request.user, status='pending', tx_type='deposit').count()
    if pending_count >= 3:
        messages.error(request, "You have too many pending requests. Please wait for admin approval.")
        return redirect('transactions:history')

    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            deposit = form.save(commit=False)
            deposit.user = request.user
            deposit.tx_type = 'deposit'
            deposit.status = 'pending'
            deposit.save()
            messages.success(request, "Deposit request submitted successfully! Pending admin review.")
            return redirect('transactions:history')
    else:
        form = DepositForm()
    
    wallet_address = getattr(settings, 'TRON_WALLET_ADDRESS', "TBy5YFjUKjmCwLzdt3YoqjBpf493qVNrim")
    return render(request, 'transactions/deposit.html', {
        'form': form,
        'wallet_address': wallet_address,
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
            
            request.user.balance -= withdraw.amount
            request.user.save()
            
            withdraw.save()
            messages.success(request, "Withdrawal request submitted. Funds are locked until approval.")
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