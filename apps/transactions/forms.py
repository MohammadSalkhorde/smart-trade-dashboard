from django import forms
from .models import Transaction

class DepositForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'tx_hash']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'tx_hash': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter Transaction Hash (TXID)'
            }),
        }

class WithdrawForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'tx_hash']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Min 10.00 USDT',
                'step': '0.01'
            }),
            'tx_hash': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Paste your TRC20 Wallet Address (T...)'
            }),
        }

    def __init__(self, *args, **kwargs):
        # دریافت کاربر برای بررسی موجودی در متد clean
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        
        # ۱. بررسی مثبت بودن مبلغ
        if amount is not None and amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
            
        # ۲. بررسی موجودی کاربر
        if self.user and amount is not None:
            if amount > self.user.balance:
                raise forms.ValidationError(f"Insufficient balance! Your current balance is ${self.user.balance}")
        
        # ۳. حداقل مبلغ برداشت (اختیاری - مثال: ۱۰ دلار)
        if amount is not None and amount < 10:
            raise forms.ValidationError("Minimum withdrawal amount is 10 USDT.")
            
        return amount