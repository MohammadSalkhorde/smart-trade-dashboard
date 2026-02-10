from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name="Email Address")
    
    balance = models.DecimalField(
        max_digits=20, 
        decimal_places=2, 
        default=0.00,
        verbose_name="Total Balance (USDT)"
    )
    
    wallet_address = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        verbose_name="User Wallet Address"
    )

    is_verified = models.BooleanField(default=True)
    
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    referral_code = models.CharField(max_length=10, unique=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
            
        if not self.referral_code:
            self.referral_code = str(uuid.uuid4())[:8]
        super().save(*args, **kwargs)
        
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email

    @property
    def total_withdrawals(self):
        return self.transaction_set.filter(tx_type='withdraw', status='approved').aggregate(
            models.Sum('amount'))['amount__sum'] or 0

    @property
    def total_deposits(self):
        return self.transaction_set.filter(tx_type='deposit', status='approved').aggregate(
            models.Sum('amount'))['amount__sum'] or 0
    
    @property
    def referral_earnings(self):
        """
        نمایش ۱۰ درصد از تمام واریزی‌های تایید شده زیرمجموعه‌ها در داشبورد
        """
        from apps.transactions.models import Transaction
        my_referrals = User.objects.filter(referred_by=self)
        
        total_deposited = Transaction.objects.filter(
            user__in=my_referrals,
            tx_type='deposit',
            status='approved'
        ).aggregate(models.Sum('amount'))['amount__sum'] or 0
        
        # تغییر از 0.05 به 0.10 برای هماهنگی با واریز واقعی
        return round(float(total_deposited) * 0.10, 2)

class Notification(models.Model):
    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE) 
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.email}"