from django.contrib import admin
from .models import TradingPair, LeadTrader

@admin.register(TradingPair)
class TradingPairAdmin(admin.ModelAdmin):
    # نمایش فیلدها در جدول ادمین
    list_display = ('display_name', 'symbol', 'real_price', 'manipulation_percent', 'display_price')
    # قابلیت ویرایش مستقیم درصد دستکاری از داخل جدول بدون باز کردن صفحه جدید
    list_editable = ('manipulation_percent',)

@admin.register(LeadTrader)
class LeadTraderAdmin(admin.ModelAdmin):
    list_display = ('name', 'roi_30d', 'followers_count', 'aum')