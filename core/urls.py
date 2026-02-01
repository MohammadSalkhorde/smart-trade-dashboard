from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # متصل کردن یو‌ار‌ال‌های اپلیکیشن تریدینگ
    path('trading/', include('apps.trading.urls')),
    
    # متصل کردن یو‌ار‌ال‌های اپلیکیشن اکانت (در آینده)
    path('accounts/', include('apps.accounts.urls')),
    
    # متصل کردن یو‌ار‌ال‌های اپلیکیشن تراکنش (در آینده)
    path('transactions/', include('apps.transactions.urls')),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)