from django.urls import path
from .views import *

app_name = 'accounts'

urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('profile/', user_dashboard, name='profile_dashboard'),
    path('dashboard/', profile_dashboard, name='dashboard'),
    path('notifications/read/<int:pk>/', mark_notification_as_read, name='mark_notification_read'),
    path('about/', about_us, name='about_us'),
    path('contact/', contact_us, name='contact_us'), 
    path('terms/', terms_conditions, name='terms_conditions'),
]