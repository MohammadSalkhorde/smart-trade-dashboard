from django.urls import path
from .views import deposit_view, withdraw_view, transaction_history

app_name = 'transactions'

urlpatterns = [
    path('deposit/', deposit_view, name='deposit'),
    path('withdraw/', withdraw_view, name='withdraw'),
    path('history/', transaction_history, name='history'),
]