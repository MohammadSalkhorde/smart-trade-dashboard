from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class User(AbstractUser):
    # اجباری و یکتا کردن ایمیل برای جایگزینی با یوزرنیم
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

    # تنظیم ایمیل به عنوان فیلد اصلی برای لاگین
    USERNAME_FIELD = 'email'
    # فیلدهایی که موقع createsuperuser پرسیده می‌شوند (یوزرنیم اینجا اجباری می‌ماند)
    REQUIRED_FIELDS = ['username']


    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = str(uuid.uuid4())[:8] # تولید کد دعوت یکتا
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
        
        
class Notification(models.Model):
    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE) 
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.email}"