from pathlib import Path
import os

# --- Basic Config ---
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-*xmm7ru+t1&@nrc3+piqq^26qlwku7mmp*a^tprjm7^jb)!b8k')

DEBUG = False

ALLOWED_HOSTS = [
    'smartcopytraders.com', 
    'www.smartcopytraders.com', 
    'smartcopytrader.com', 
    'www.smartcopytrader.com', 
    '91.107.154.232',
    '127.0.0.1',
    'localhost'
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
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
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

# --- PRODUCTION SECURITY SETTINGS (Cloudflare Optimized) ---

# این خط به جنگو می‌گوید که پشت یک پروکسی (کلودفلر) است و باید HTTPS را تشخیص دهد
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# لیست دامنه‌های معتبر برای جلوگیری از ارور CSRF
CSRF_TRUSTED_ORIGINS = [
    'https://smartcopytraders.com',
    'https://www.smartcopytraders.com',
    'https://smartcopytrader.com',
    'https://www.smartcopytrader.com'
]

# اجباری کردن ریدایرکت به HTTPS
SECURE_SSL_REDIRECT = True

# امنیت کوکی‌ها (وقتی روی HTTPS هستیم باید True باشند)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# تنظیمات هدرهای امنیتی
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'