from django.urls import path
from .views import *

app_name = 'trading'

urlpatterns = [
    path('copy-trading/', copy_trading_dashboard, name='copy_list'),
    path('market/', market_list, name='market_list'),
]