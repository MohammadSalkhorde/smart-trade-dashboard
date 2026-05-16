from pathlib import Path
import os

# --- Basic Config ---
BASE_DIR = Path(__file__).resolve().parent.parent

# امنیت: حتماً در محیط سرور یک کلید اختصاصی تعریف کن، در غیر این صورت از این دیفالت استفاده می‌شود
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-prod-smarter-copy-trade-key-2026')

# غیرفعال کردن دیباگ برای امنیت و کارایی
DEBUG = True

ALLOWED_HOSTS = [
    'smartercopytrade.com', 
    'www.smartercopytrade.com',
    '154.29.76.222',  # آی‌پی جدید شما
    '127.0.0.1',
    'localhost',
]

# --- Apps & Models ---
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

# --- Middleware ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', 
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

# --- Database ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --- Password Validation ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# --- Internationalization ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --- Static & Media Files ---
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- PRODUCTION & CLOUDFLARE SECURITY ---

# شناسایی HTTPS از سمت کلودفلر
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# دامنه‌های مورد اعتماد برای CSRF
CSRF_TRUSTED_ORIGINS = [
    'https://smartercopytrade.com',
    'https://www.smartercopytrade.com',
]

SECURE_SSL_REDIRECT = False 
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# سایر تنظیمات امنیتی
SESSION_COOKIE_HTTPONLY = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'


TRONGRID_API_KEY = ""
TRONGRID_API_URL = "https://api.trongrid.io"
MASTER_WALLET_ADDRESS = "TBy5YFjUKjmCwLzdt3YoqjBpf493qVNrim"
MIN_BALANCE_TO_SWEEP = 5