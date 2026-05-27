import re
from django import forms
from django.core.exceptions import ValidationError
from .models import Transaction

class DepositForm(forms.ModelForm):
    NETWORK_CHOICES = [
        ('TRC20', 'TRC20'),
        ('BEP20', 'BEP20'),
    ]
    network = forms.ChoiceField(
        choices=NETWORK_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True,
        label="Network"
    )

    class Meta:
        model = Transaction
        fields = ['network', 'amount', 'tx_hash']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'min': '3',  # اصلاح شد: حداقل واریز به 3 تغییر یافت
                'step': '0.01'
            }),
            'tx_hash': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter TXID / Transaction Hash',
                'maxlength': '255',
            }),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None:
            if amount <= 0:
                raise ValidationError("Amount must be greater than zero.")
            if amount < 3:
                raise ValidationError("Minimum deposit is 3 USDT.")
        return amount

    def clean(self):
        """
        ولیدیشن ساختار هش تراکنش (TXID) متناسب با شبکه انتخاب شده در سمت بک‌اند
        """
        cleaned_data = super().clean()
        network = cleaned_data.get('network')
        tx_hash = cleaned_data.get('tx_hash', '')
        
        if tx_hash:
            tx_hash = tx_hash.strip()
            
            # جلوگیری از کاراکترهای مخرب اکسپلویت
            if re.search(r'[<>{}[\]\(\);|&]', tx_hash):
                self.add_error('tx_hash', "Invalid characters detected in transaction hash.")
                return cleaned_data

            # بررسی تکراری نبودن هش تراکنش
            if Transaction.objects.filter(tx_hash=tx_hash).exists():
                self.add_error('tx_hash', "This transaction hash has already been submitted.")
                return cleaned_data

            # ولیدیشن ساختار هش بر اساس شبکه (TRC20 یا BEP20)
            if network == 'TRC20':
                # هش تراکنش ترون حتماً باید یک رشته هگز 64 کاراکتری باشد
                if not re.match(r'^[a-fA-F0-9]{64}$', tx_hash):
                    self.add_error('tx_hash', "Invalid TRC20 TXID format. It must be a 64-character hex string.")
            
            elif network == 'BEP20':
                # هش تراکنش بایننس اسمارت چین با 0x شروع شده و شامل 64 کاراکتر هگز است
                if not re.match(r'^0x[a-fA-F0-9]{64}$', tx_hash):
                    self.add_error('tx_hash', "Invalid BEP20 Hash format. It must start with '0x' followed by 64 hex characters.")
        
        return cleaned_data


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
                'placeholder': 'Enter your USDT Destination Wallet Address'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['tx_hash'].label = "Your Wallet Address"

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None:
            if amount < 10:
                raise ValidationError("Minimum withdrawal amount is 10 USDT.")
            if self.user and amount > self.user.balance:
                raise ValidationError(f"Insufficient balance! Current: ${self.user.balance}")
        return amount

    def clean_tx_hash(self):
        """
        پاکسازی و ولیدیشن اولیه فیلد آدرس ولت
        """
        address = self.cleaned_data.get('tx_hash', '')
        if not address:
            raise ValidationError("Wallet address is required for withdrawal.")
        return address.strip()

    def clean(self):
        """
        بررسی هماهنگی فرمت آدرس ولت با شبکه انتخابی برداشت
        """
        cleaned_data = super().clean()
        network = cleaned_data.get('network')
        address = cleaned_data.get('tx_hash')

        # تنها در صورتی بررسی انجام می‌شود که خود فیلدها در مراحل قبلی خطا نداشته باشند
        if network and address:
            address = address.strip()
            
            if network == 'TRC20':
                # آدرس‌های ترون با T شروع شده و 34 کاراکتر با فرمت Base58 هستند
                if not re.match(r'^T[a-km-zA-HJ-NP-Z1-9]{33}$', address):
                    self.add_error('tx_hash', "Invalid TRC20 address format.")
            
            elif network == 'BEP20':
                # آدرس‌های شبکه هوشمند بایننس با 0x شروع شده و طول آن 42 کاراکتر است (0x + 40 کاراکتر هگز)
                if not re.match(r'^0x[a-fA-F0-9]{40}$', address):
                    self.add_error('tx_hash', "Invalid BEP20 address format.")
        
        return cleaned_data