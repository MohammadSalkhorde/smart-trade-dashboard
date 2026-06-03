# apps/accounts/middleware.py
from django.utils import translation

class ForceEnglishMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # اجبار به استفاده از زبان انگلیسی برای تمام درخواست‌ها
        translation.activate('en-us')
        request.LANGUAGE_CODE = 'en-us'
        
        response = self.get_response(request)
        return response