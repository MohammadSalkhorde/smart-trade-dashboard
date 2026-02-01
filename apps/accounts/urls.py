from django.urls import path
from .views import *

app_name = 'accounts'

urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', user_dashboard, name='dashboard'),
    path('profile/', profile_dashboard, name='profile_dashboard'),
]