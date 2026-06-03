# decorators.py
from django.core.exceptions import PermissionDenied
from functools import wraps

def block_banned_users(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_banned:
            # اینجا ما ویو را اجرا نمی‌کنیم و ارور ۴۰۳ می‌دهیم
            raise PermissionDenied 
        return view_func(request, *args, **kwargs)
    return _wrapped_view