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

class WithdrawForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'tx_hash'] # اینجا از tx_hash برای گرفتن آدرس ولت کاربر استفاده می‌کنیم
        labels = {
            'tx_hash': 'Your Wallet Address (TRC20)',
            'amount': 'Withdraw Amount (USDT)'
        }
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tx_hash': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'T...'})
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if self.user and amount > self.user.balance:
            raise forms.ValidationError("Insufficient balance!")
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount