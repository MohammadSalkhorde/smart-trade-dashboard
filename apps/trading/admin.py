from django.contrib import admin
from .models import TradingPair, LeadTrader

@admin.register(TradingPair)
class TradingPairAdmin(admin.ModelAdmin):
    # نمایش فیلدها در جدول ادمین
    list_display = ('display_name', 'symbol', 'real_price', 'manipulation_percent', 'display_price')
    # قابلیت ویرایش مستقیم درصد دستکاری از داخل جدول بدون باز کردن صفحه جدید
    list_editable = ('manipulation_percent',)
# apps/trading/admin.py

@admin.register(LeadTrader)
class LeadTraderAdmin(admin.ModelAdmin):
    # مقدار followers_count را با followers_count_manual یا copiers_count جایگزین کن
    list_display = ('name', 'roi_30d', 'followers_count_manual', 'win_rate', 'risk_level') 
    # اگر فیلدهای دیگر هم ارور دادند، مطمئن شو نامشان با مدل جدید یکی است