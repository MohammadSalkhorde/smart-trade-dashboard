from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    # متصل کردن یو‌ار‌ال‌های اپلیکیشن تریدینگ
    path('trading/', include('apps.trading.urls')),
    
    # متصل کردن یو‌ار‌ال‌های اپلیکیشن اکانت (در آینده)
    path('accounts/', include('apps.accounts.urls')),
    
    # متصل کردن یو‌ار‌ال‌های اپلیکیشن تراکنش (در آینده)
    path('transactions/', include('apps.transactions.urls')),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.contrib import admin

admin.site.site_header = "SmartTrade Management" # عنوان بالای صفحه
admin.site.site_title = "SmartTrade Admin Portal" # عنوان تب مرورگر
admin.site.index_title = "Welcome to the Trading Control Center" # عنوان صفحه اصلی ادمین