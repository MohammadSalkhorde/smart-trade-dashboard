from django.urls import path
from .views import *

app_name = 'trading'

urlpatterns = [
    path('copy-trading/', copy_trading_dashboard, name='copy_list'),
    path('market/', market_list, name='market_list'),
    path('copy/<int:trader_id>/', copy_action, name='copy_action'),
    path('stop-copy/<int:follow_id>/', stop_copy_action, name='stop_copy_action'),
    path('trader/<int:trader_id>/', trader_detail, name='trader_detail'),
]