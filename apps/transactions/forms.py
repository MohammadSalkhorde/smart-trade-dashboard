from django import forms
from .models import Transaction

class DepositForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'tx_hash']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Amount in USDT'}),
            'tx_hash': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Transaction Hash (TXID)'}),
        }