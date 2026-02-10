from django.db import models
from django.conf import settings
import random

class SystemSettings(models.Model):
    """تنظیمات کلان سایت"""
    tron_wallet_address = models.CharField(max_length=255, default="TBy5YFjUKjmCwLzdt3YoqjBpf493qVNrim")
    min_deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=10.0)
    site_name = models.CharField(max_length=100, default="SmartTrade")

    class Meta:
        verbose_name = "System Setting"
        verbose_name_plural = "System Settings"

    def __str__(self):
        return "Global System Settings"


class TradingPair(models.Model):
    """مدل ارزها با قابلیت دستکاری قیمت لحظه‌ای"""
    symbol = models.CharField(max_length=20, unique=True, help_text="Example: BTC/USDT")
    display_name = models.CharField(max_length=50, help_text="The random name (e.g., Alpha Strategy)")
    real_price = models.DecimalField(max_digits=20, decimal_places=8, default=0.0)
    
    # ضریب دستکاری لحظه‌ای (درصد)
    manipulation_percent = models.FloatField(default=0.0, help_text="Manual offset percentage") 
    
    # رشد روزانه هدف
    daily_growth_percent = models.FloatField(default=0.0, help_text="Admin's target daily growth")
    
    is_active = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)

    nickname = models.CharField(max_length=100, blank=True, null=True) 

    @property
    def final_display_name(self):
        return self.nickname if self.nickname else self.display_name
    
    @property
    def display_price(self):
        if not self.real_price:
            return 0.0
        adjustment = (float(self.real_price) * self.manipulation_percent) / 100
        return float(self.real_price) + adjustment

    def __str__(self):
        return f"{self.display_name} ({self.symbol})"


class LeadTrader(models.Model):
    """مدل تریدر با سیستم مدیریت چارت (مشابه BingX)"""
    name = models.CharField(max_length=100)
    avatar = models.ImageField(upload_to='traders/', blank=True, null=True)
    
    # آمارهای نمایشی و واقعی
    roi_30d = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    pnl_30d = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    aum = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    max_drawdown = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    
    win_rate = models.IntegerField(default=85)
    risk_level = models.IntegerField(default=3)
    followers_count_manual = models.IntegerField(default=0, help_text="فالوورهای فیک برای جذابیت")
    capacity = models.IntegerField(default=100)
    
    # مدیریت چارت
    chart_history_json = models.JSONField(default=list, help_text="تاریخچه سودها برای رسم نمودار")
    target_profit_growth = models.FloatField(default=0.0, help_text="عددی که طی ۷ روز به چارت اضافه می‌شود")

    is_manual_mode = models.BooleanField(
        default=False, 
        help_text="If checked, the chart will use Admin's points instead of Binance live data."
    )
    
    @property
    def total_copiers(self):
        return self.followed_traders.count() + self.followers_count_manual

    def add_profit_point(self, percentage):
        """متد کلیدی برای اضافه کردن نقطه به نمودار و آپدیت ROI"""
        history = list(self.chart_history_json)
        if not history: history = [0.0]
        
        new_point = round(float(history[-1]) + float(percentage), 2)
        history.append(new_point)
        
        self.chart_history_json = history[-30:] # فقط ۳۰ روز آخر
        self.roi_30d = new_point
        self.save()
        
    # Trading App - models.py - کلاس LeadTrader

    def update_chart_by_profit(self):
        """هماهنگ سازی چارت با درصد سود ادمین"""
        history = list(self.chart_history_json)
        # اگر ادمین عدد سود را دستی تغییر داد، چارت را آپدیت کن
        if history:
            history[-1] = float(self.roi_30d)
            self.chart_history_json = history
            self.save()

    def __str__(self):
        return f"{self.name} (ROI: {self.roi_30d}%)"


class FollowedTrader(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='followed_traders_list')
    trader = models.ForeignKey(LeadTrader, on_delete=models.CASCADE, related_name='followed_traders')
    investment_amount = models.DecimalField(max_digits=20, decimal_places=2)
    
    # --- فیلد جدید برای حل مشکل رفرش ---
    entry_price = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    last_pnl = models.DecimalField(max_digits=10, decimal_places=4, default=0.0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    entry_roi = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    
    def __str__(self):
        return f"{self.user.username} کپی از {self.trader.name}"
    
class Deposit(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    tx_hash = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} USDT"