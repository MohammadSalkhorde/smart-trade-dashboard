from django.db import models
from django.conf import settings
from decimal import Decimal

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
    currency = models.CharField(max_length=10, default='USDT')
    tx_hash = models.CharField(max_length=255) 
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.tx_type} - {self.amount}"

    def save(self, *args, **kwargs):
        if self.pk:
            old_status = Transaction.objects.filter(pk=self.pk).values_list('status', flat=True).first()
            
            if old_status == 'pending':

                if self.status == 'approved' and self.tx_type == 'deposit':
                    user = self.user
                    user.balance += self.amount
                    user.save()
                    
                    if user.referred_by:
                        referrer = user.referred_by

                        referral_bonus = self.amount * Decimal('0.10')
                        referrer.balance += referral_bonus
                        referrer.save()
                        
                        try:
                            from apps.accounts.models import Notification

                            Notification.objects.create(
                                user=referrer,
                                message=f"You earned ${referral_bonus:.2f} referral bonus from {user.email}'s deposit!"
                            )
                        except ImportError:
                            pass


                elif self.status == 'rejected' and self.tx_type == 'withdraw':
                    user = self.user
                    user.balance += self.amount
                    user.save()
        
        super().save(*args, **kwargs)