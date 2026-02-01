from django.db import models
from django.conf import settings

class TradingPair(models.Model):
    """مدل ارزها با قابلیت دستکاری قیمت لحظه‌ای"""
    symbol = models.CharField(max_length=20, unique=True, help_text="Example: BTC/USDT")
    display_name = models.CharField(max_length=50, help_text="The random name user requested")
    real_price = models.DecimalField(max_digits=20, decimal_places=8, default=0.0)
    
    # ضریب دستکاری: مثلا 2.5 یعنی 2.5 درصد قیمت را بالاتر نشان بده
    manipulation_percent = models.FloatField(default=0.0) 
    
    is_active = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)

    @property
    def display_price(self):
        """قیمتی که با احتساب دستکاری ادمین در سایت نمایش داده می‌شود"""
        adjustment = (float(self.real_price) * self.manipulation_percent) / 100
        return float(self.real_price) + adjustment

    def __str__(self):
        return f"{self.display_name} ({self.symbol})"

class LeadTrader(models.Model):
    """مدل تریدرهای حرفه‌ای برای بخش Copy Trading"""
    name = models.CharField(max_length=100)
    avatar = models.ImageField(upload_to='traders/', blank=True, null=True)
    
    # آمارهای ۳۰ روزه طبق ظاهر BingX
    roi_30d = models.DecimalField(max_digits=10, decimal_places=2, help_text="ROI Percentage")
    pnl_30d = models.DecimalField(max_digits=20, decimal_places=2, help_text="Total Profit in USDT")
    aum = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="Assets Under Management")
    max_drawdown = models.DecimalField(max_digits=5, decimal_places=2)
    
    followers_count = models.IntegerField(default=0)
    capacity = models.IntegerField(default=100) # ظرفیت کپی کردن
    
    # دیتای نمودار کوچک خطی (بصورت لیست اعداد برای نمایش در فرانت)
    chart_history_json = models.JSONField(default=list, help_text="List of values for mini chart")

    def __str__(self):
        return self.name