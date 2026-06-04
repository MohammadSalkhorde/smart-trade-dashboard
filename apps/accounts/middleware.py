# apps/accounts/middleware.py
from django.utils import translation
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied

class ForceEnglishMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        translation.activate('en-us')
        request.LANGUAGE_CODE = 'en-us'
        response = self.get_response(request)
        return response


class BannedUserRestrictionMiddleware:
    """
    اگر کاربر بن شده باشد، سایت بالا می‌آید (GET)، 
    اما هرگونه عملیات هجومی یا ارسال فرم (POST, PUT, DELETE) بلافاصله بلاک می‌شود.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and getattr(request.user, 'is_banned', False):
            # اگر درخواست از نوع ارسال فرم یا عملیات بود (غیر از لود کردن ساده صفحه)
            if request.method != 'GET':
                # اگر درخواست سمت فرانت با Fetch یا Ajax/Axios بود، جیسون برگردان
                if request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', ''):
                    return JsonResponse({
                        'status': 'error',
                        'message': 'REGIONAL_COMPLIANCE_LOCK: Access denied from your current IP routing.'
                    }, status=403)
                
                # برای درخواست‌های معمولی ارور عدم دسترسی بده
                raise PermissionDenied

        response = self.get_response(request)
        return response