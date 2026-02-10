from django import forms
from .models import Transaction
import re
from django import forms
from django.core.exceptions import ValidationError

class DepositForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'tx_hash']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': '0.00',
                'min': '1',
            }),
            'tx_hash': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter 64-character TXID',
                'maxlength': '64',
            }),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise ValidationError("Amount must be greater than zero.")
        if amount > 1000000:
            raise ValidationError("Invalid amount. Please contact support for large deposits.")
        return amount

    def clean_tx_hash(self):
        tx_hash = self.cleaned_data.get('tx_hash').strip()
        

        if re.search(r'[<>{}[\]\(\);|&]', tx_hash):
            raise ValidationError("Invalid characters detected in transaction hash.")


        if not re.match(r'^[a-fA-F0-9]{64}$', tx_hash):
            raise ValidationError("Invalid TXID format. Must be a 64-character hex string.")


        if Transaction.objects.filter(tx_hash=tx_hash).exists():
            raise ValidationError("This transaction hash has already been submitted.")
            
        return tx_hash

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

        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        
        if amount is not None and amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
            
        if self.user and amount is not None:
            if amount > self.user.balance:
                raise forms.ValidationError(f"Insufficient balance! Your current balance is ${self.user.balance}")
        
        if amount is not None and amount < 10:
            raise forms.ValidationError("Minimum withdrawal amount is 10 USDT.")
            
        return amount