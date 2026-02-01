from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    مدل سفارشی کاربر برای مدیریت موجودی و اطلاعات صرافی
    """
    # موجودی کاربر به تتر (USDT) - برای دقت بالا از Decimal استفاده شده
    balance = models.DecimalField(
        max_digits=20, 
        decimal_places=2, 
        default=0.00,
        verbose_name="Total Balance (USDT)"
    )
    
    # آدرس ولت کاربر (اختیاری - برای نمایش در پروفایل)
    wallet_address = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        verbose_name="User Wallet Address"
    )

    # فیلد تاییدیه کاربر (اگر بعدا نیاز به احراز هویت بود)
    is_verified = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username

    @property
    def total_withdrawals(self):
        """محاسبه مجموع برداشت‌های تایید شده کاربر"""
        return self.transaction_set.filter(tx_type='withdraw', status='approved').aggregate(
            models.Sum('amount'))['amount__sum'] or 0

    @property
    def total_deposits(self):
        """محاسبه مجموع واریزی‌های تایید شده کاربر"""
        return self.transaction_set.filter(tx_type='deposit', status='approved').aggregate(
            models.Sum('amount'))['amount__sum'] or 0