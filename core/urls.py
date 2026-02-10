from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),

    path('trading/', include('apps.trading.urls')),
    
    path('accounts/', include('apps.accounts.urls')),
    
    path('transactions/', include('apps.transactions.urls')),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.contrib import admin

admin.site.site_header = "SmartTrade Management" 
admin.site.site_title = "SmartTrade Admin Portal" 
admin.site.index_title = "Welcome to the Trading Control Center" 