from django.contrib import admin
from .models import TradingPair, LeadTrader

@admin.register(TradingPair)
class TradingPairAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'symbol', 'real_price', 'manual_profit_percent', 'manipulated_price')
    list_editable = ('manual_profit_percent',) # اجازه ادیت سریع درصد در لیست

@admin.register(LeadTrader)
class LeadTraderAdmin(admin.ModelAdmin):
    list_display = ('name', 'roi_30d', 'followers_count', 'aum')