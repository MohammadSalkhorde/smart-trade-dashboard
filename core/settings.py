from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# امنیت: در محیط سرور بهتر است از Environment Variable استفاده شود
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-*xmm7ru+t1&@nrc3+piqq^26qlwku7mmp*a^tprjm7^jb)!b8k')

# در حالت پروداکشن حتما False باشد
DEBUG = False

ALLOWED_HOSTS = [
    'smartcopytraders.com', 
    'www.smartcopytraders.com',
    'smartcopytrader.com', 
    'www.smartcopytrader.com', 
    '91.107.154.232', 
    'localhost', 
    '127.0.0.1'
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'apps.accounts.apps.AccountsConfig',
    'apps.trading.apps.TradingConfig',
    'apps.transactions.apps.TransactionsConfig',
]

AUTH_USER_MODEL = 'accounts.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # برای مدیریت فایل‌های استاتیک در حالت DEBUG=False
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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# تنظیمات فایل‌های استاتیک
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# نکته: اگر پوشه static در پروژه نداری، این خط را کامنت کن تا ارور ندهد
# STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# تنظیمات فایل‌های رسانه‌ای (آپلودها)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# تنظیمات امنیتی برای دامنه و آی‌پی
CSRF_TRUSTED_ORIGINS = [
    'http://smartcopytraders.com',
    'http://www.smartcopytraders.com',
    'http://smartcopytrader.com',
    'http://www.smartcopytrader.com',
    'http://91.107.154.232'
]
# اگر از HTTPS استفاده نمی‌کنید این دو مورد را فعلا False بگذارید تا لاگین به مشکل نخورد
SESSION_COOKIE_SECURE = False 
CSRF_COOKIE_SECURE = False

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'