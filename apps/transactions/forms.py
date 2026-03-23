from django import forms
from .models import Transaction
from django.core.exceptions import ValidationError
import re

class DepositForm(forms.ModelForm):
    # انتخاب شبکه - این فیلد نباید خالی بماند
    NETWORK_CHOICES = [
        ('TRC20', 'TRC20 (Tron)'),
        ('BEP20', 'BEP20 (Binance Smart Chain)'),
    ]
    network = forms.ChoiceField(
        choices=NETWORK_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'networkSelect'}),
        required=True
    )

    class Meta:
        model = Transaction
        fields = ['network', 'amount', 'tx_hash'] # ترتیب فیلدها اصلاح شد
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': '0.00',
                'min': '1',
            }),
            'tx_hash': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter 64-character TXID',
                'maxlength': '66', # برای پشتیبانی از 0x در ابتدای هش های BEP20
            }),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise ValidationError("Amount must be greater than zero.")
        return amount

    def clean_tx_hash(self):
        tx_hash = self.cleaned_data.get('tx_hash', '').strip()
        
        if re.search(r'[<>{}[\]\(\);|&]', tx_hash):
            raise ValidationError("Invalid characters detected in transaction hash.")

        # بررسی فرمت هش (هگزادسیمال 64 کاراکتری با یا بدون 0x)
        clean_hash = tx_hash[2:] if tx_hash.startswith('0x') else tx_hash
        if not re.match(r'^[a-fA-F0-9]{64}$', clean_hash):
            raise ValidationError("Invalid TXID format. Must be a 64-character hex string.")

        if Transaction.objects.filter(tx_hash=tx_hash).exists():
            raise ValidationError("This transaction hash has already been submitted.")
            
        return tx_hash

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