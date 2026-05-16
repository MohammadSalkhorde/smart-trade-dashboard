from django import forms
from .models import Transaction
from django.core.exceptions import ValidationError
import re

class DepositForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter amount (min 10 USDT)',
                'min': '10',
                'step': '0.01'
            }),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount and amount < 10:
            from django.core.exceptions import ValidationError
            raise ValidationError("Minimum deposit is 10 USDT")
        return amount

class WithdrawForm(forms.ModelForm):
    NETWORK_CHOICES = [
        ('TRC20', 'TRC20'),
        ('BEP20', 'BEP20'),
    ]
    network = forms.ChoiceField(
        choices=NETWORK_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}), 
        required=True
    )

    class Meta:
        model = Transaction
        fields = ['network', 'amount', 'tx_hash']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Min 10.00 USDT',
                'step': '0.01'
            }),
            'tx_hash': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter your USDT Wallet Address'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        network = cleaned_data.get('network')
        address = cleaned_data.get('tx_hash')

        if network == 'TRC20' and address:
            if not address.startswith('T') or len(address) < 30:
                raise ValidationError({'tx_hash': "Invalid TRC20 address format. Should start with 'T'"})
        
        elif network == 'BEP20' and address:
            if not address.startswith('0x') or len(address) < 40:
                raise ValidationError({'tx_hash': "Invalid BEP20 address format. Should start with '0x'"})
        
        return cleaned_data

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None:
            if amount < 10:
                raise ValidationError("Minimum withdrawal amount is 10 USDT.")
            if self.user and amount > self.user.balance:
                raise ValidationError(f"Insufficient balance! Current: ${self.user.balance}")
        return amount