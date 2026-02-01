from django.urls import path
from .views import copy_trading_dashboard # نام ویو رو چک کن که همین باشه

app_name = 'trading'

urlpatterns = [
    # آدرس نهایی میشه: /trading/copy-trading/
    path('copy-trading/', copy_trading_dashboard, name='copy_list'),
]