from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    path('deposit/', views.deposit_view, name='deposit'),
    path('withdraw/', views.withdraw_view, name='withdraw'),
    path('history/', views.transaction_history, name='history'),
    path('transactions/<int:pk>/', views.transaction_detail, name='transaction_detail'),
]