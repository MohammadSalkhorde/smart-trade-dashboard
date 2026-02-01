from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import DepositForm
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
            return redirect('transactions:history')
    else:
        form = DepositForm()
    
    # آدرس ولت ثابت شما که کاربر باید به آن واریز کند
    admin_wallet = "T9yD14Nj9j7xXh4LkTo7993sh9sh9sh9sh" # این را با ولت واقعی جایگزین کن
    return render(request, 'transactions/deposit.html', {'form': form, 'wallet': admin_wallet})

@login_required
def transaction_history(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'transactions/history.html', {'transactions': transactions})