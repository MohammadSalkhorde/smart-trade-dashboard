from django.db import models
from django.conf import settings

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('deposit', 'Deposit'),
        ('withdraw', 'Withdraw'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tx_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    currency = models.CharField(max_length=10, default='USDT') # معمولاً تتر استفاده میشه
    
    # برای واریز میشه TXID و برای برداشت میشه آدرس ولت مقصد
    tx_hash = models.CharField(max_length=255) 
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.tx_type} - {self.amount}"

    def save(self, *args, **kwargs):
            if self.pk:
                # گرفتن وضعیت قبلی از دیتابیس
                old_transaction = Transaction.objects.get(pk=self.pk)
                
                # حالت ۱: تایید واریز (Deposit Approved)
                if old_transaction.status == 'pending' and self.status == 'approved':
                    if self.tx_type == 'deposit':
                        # اضافه کردن موجودی به خود کاربر
                        self.user.balance += self.amount
                        self.user.save()
                        
                        # منطق سود ۱۰ درصدی زیرمجموعه (Referral System)
                        if hasattr(self.user, 'referred_by') and self.user.referred_by:
                            from decimal import Decimal
                            referral_bonus = self.amount * Decimal('0.10')
                            self.user.referred_by.balance += referral_bonus
                            self.user.referred_by.save()
                
                # حالت ۲: رد شدن برداشت (Withdraw Rejected) -> پول باید به موجودی کاربر برگردد
                elif old_transaction.status == 'pending' and self.status == 'rejected':
                    if self.tx_type == 'withdraw':
                        self.user.balance += self.amount
                        self.user.save()
            
            super().save(*args, **kwargs)