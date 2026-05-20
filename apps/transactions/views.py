import requests
import json
import hmac
import hashlib
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from .forms import DepositForm, WithdrawForm
from .models import Transaction
from apps.trading.models import SystemSettings
from apps.accounts.models import User

# ==================== NOWPAYMENTS SERVICES ====================

class NowPaymentsService:
    BASE_URL = "https://api.nowpayments.io/v1"

    def __init__(self):
        self.api_key = settings.NOWPAYMENTS_API_KEY

    def _get_headers(self):
        return {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }

    def create_payment(self, user, amount_usd):
        """ایجاد درخواست پرداخت و دریافت آدرس اختصاصی"""
        if amount_usd < 10:
            raise ValueError("Minimum deposit is 10 USDT")

        payload = {
            "price_amount": float(amount_usd),
            "price_currency": "usd",
            "pay_currency": "usdttrc20",
            "order_id": f"user_{user.id}_{user.username}",
            "order_description": f"Deposit for {user.email}",
            "is_fee_paid_by_user": True,
        }

        response = requests.post(
            f"{self.BASE_URL}/payment",
            json=payload,
            headers=self._get_headers(),
            timeout=30
        )
        
        if response.status_code == 201:
            data = response.json()
            return {
                "payment_id": data["payment_id"],
                "pay_address": data["pay_address"],
                "pay_amount": Decimal(str(data["pay_amount"])),
                "status": data["payment_status"]
            }
        else:
            error_msg = response.json().get('message', 'Unknown error')
            raise Exception(f"NowPayments error: {error_msg}")

    def get_payment_status(self, payment_id):
        """بررسی وضعیت پرداخت"""
        url = f"{self.BASE_URL}/payment/{payment_id}"
        response = requests.get(url, headers=self._get_headers(), timeout=15)
        if response.status_code == 200:
            return response.json()
        return None


# ==================== DEPOSIT VIEW ====================

@login_required
def deposit_view(request):
    # بررسی درخواست pending قبلی (با استفاده از Transaction)
    pending_deposit = Transaction.objects.filter(
        user=request.user, 
        status='pending', 
        tx_type='deposit'
    ).first()
    
    pending_payment = None
    if pending_deposit and pending_deposit.tx_hash and pending_deposit.tx_hash.startswith('NP_'):
        pending_payment = {
            'pay_address': pending_deposit.network,  # آدرس در network ذخیره شده
            'pay_amount': pending_deposit.amount,
            'payment_id': pending_deposit.tx_hash.replace('NP_', ''),
            'status': 'pending'
        }

    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            
            try:
                service = NowPaymentsService()
                payment = service.create_payment(request.user, float(amount))
                
                # ذخیره در Transaction با وضعیت pending
                deposit = Transaction.objects.create(
                    user=request.user,
                    tx_type='deposit',
                    amount=Decimal(str(amount)),
                    status='pending',
                    tx_hash=f"NP_{payment['payment_id']}",
                    network=payment['pay_address'],  # آدرس موقت در network ذخیره می‌شود
                )
                
                messages.success(
                    request, 
                    f"Send exactly {payment['pay_amount']} USDT (TRC20) to the address below. "
                    f"The payment will be credited automatically."
                )
                
                return render(request, 'transactions/deposit.html', {
                    'form': DepositForm(),
                    'payment': payment
                })
                
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
    else:
        form = DepositForm()
    
    return render(request, 'transactions/deposit.html', {
        'form': form,
        'payment': pending_payment,
        'wallet_trc20': None
    })


# ==================== WEBHOOK ====================

@csrf_exempt
def nowpayments_webhook(request):
    """Webhook دریافتی از NowPayments برای تأیید خودکار واریز"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        raw_body = request.body.decode('utf-8')
        data = json.loads(raw_body)
        
        payment_id = data.get('payment_id')
        payment_status = data.get('payment_status')
        
        print(f"Webhook received: payment_id={payment_id}, status={payment_status}")
        
        if payment_status == 'finished' and payment_id:
            # پیدا کردن تراکنش مربوطه
            transaction = Transaction.objects.filter(
                tx_hash=f"NP_{payment_id}", 
                status='pending'
            ).first()
            
            if transaction:
                # تأیید تراکنش (save() خودکار موجودی را زیاد می‌کند)
                transaction.status = 'approved'
                transaction.save()
                print(f"Transaction {transaction.id} approved for user {transaction.user.email}")
                return HttpResponse("OK", status=200)
            else:
                print(f"Transaction not found for payment_id: {payment_id}")
        
        return HttpResponse("Ignored", status=200)
        
    except Exception as e:
        print(f"Webhook error: {e}")
        return JsonResponse({'error': str(e)}, status=400)


# ==================== WITHDRAW VIEW ====================

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


# ==================== TRANSACTION HISTORY ====================

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