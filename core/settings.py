from pathlib import Path
import os

# مسیر اصلی پروژه
BASE_DIR = Path(__file__).resolve().parent.parent

# تنظیمات امنیتی (در حالت توسعه)
SECRET_KEY = 'django-insecure-*xmm7ru+t1&@nrc3+piqq^26qlwku7mmp*a^tprjm7^jb)!b8k'
DEBUG = True
ALLOWED_HOSTS = ['*','localhost','127.0.0.1']

# تعریف اپلیکیشن‌ها
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third Party Apps
    'rest_framework',

    # My Apps (Labled by Folder apps)
    'apps.accounts.apps.AccountsConfig',
    'apps.trading.apps.TradingConfig',
    'apps.transactions.apps.TransactionsConfig',
]

# تعریف مدل کاربر سفارشی (بسیار مهم برای مهندسی نرم‌افزار)
AUTH_USER_MODEL = 'accounts.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # اصلاح مسیر تمپلیت‌ها
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                
                'apps.accounts.views.user_notifications'
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# دیتابیس (استفاده از SQLite برای شروع سریع و سادگی جابجایی سورس)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# اعتبارسنجی رمز عبور
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# تنظیمات بومی‌سازی
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# فایل‌های استاتیک (CSS, JS, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# تنظیمات فایل‌های رسانه‌ای (برای آپلود احتمالی عکس تریدرها)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# تنظیمات پیش‌فرض فیلد ID
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CSRF_TRUSTED_ORIGINS = [
    'https://*.trycloudflare.com',
    'https://coleman-glenn-manor-basement.trycloudflare.com', # لینک فعلی شما
]
