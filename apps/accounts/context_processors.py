# context_processors.py
from django.contrib.auth import get_user_model

def user_ban_status(request):
    is_banned = False
    if request.user.is_authenticated:
        # همیشه از دیتابیس می‌خوانیم تا تغییرات پنل ادمین آنی اعمال شود
        User = get_user_model()
        user_obj = User.objects.filter(pk=request.user.pk).first()
        if user_obj:
            is_banned = user_obj.is_banned
    return {'is_banned': is_banned}