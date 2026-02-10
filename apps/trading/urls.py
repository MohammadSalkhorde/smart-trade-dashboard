from django.urls import path
from . import views  

app_name = 'trading'

urlpatterns = [
    path('copy-trading/', views.copy_trading_dashboard, name='copy_list'),
    path('market/', views.market_list, name='market_list'),
    path('copy/<int:trader_id>/', views.copy_action, name='copy_action'),
    path('stop-copy/<int:follow_id>/', views.stop_copy_action, name='stop_copy_action'), # اضافه کردن views.
    path('trader/<int:trader_id>/', views.trader_detail, name='trader_detail'),
    path('update-pnl/', views.update_pnl_ajax, name='update_pnl_ajax'), 
    path('update-trader-chart/<int:trader_id>/', views.update_trader_chart, name='update_chart'),
    path('get-latest-pnl/<int:follow_id>/', views.get_latest_pnl, name='get_latest_pnl'),
]