from pathlib import Path
import os

# --- Basic Config ---
BASE_DIR = Path(__file__).resolve().parent.parent

# سعی می‌کند از متغیر محیطی بخواند، اگر نبود از کلید دیفالت استفاده می‌کند
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-*xmm7ru+t1&@nrc3+piqq^26qlwku7mmp*a^tprjm7^jb)!b8k')

DEBUG = True # در زمان دیپلوی نهایی False کن

ALLOWED_HOSTS = [
    'smartcopytraders.com', 
    'www.smartcopytraders.com',
    '91.107.154.232',  # اضافه شدن آی‌پی سرور
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
    'whitenoise.middleware.WhiteNoiseMiddleware', # برای مدیریت فایل‌های استاتیک در سرور
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
# فعلاً خالی گذاشتی که برای تست راحت باشی
AUTH_PASSWORD_VALIDATORS = []

# --- Internationalization ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --- Static & Media Files ---
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# ذخیره‌سازی بهینه برای سرعت بیشتر در سرور
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- PRODUCTION & CLOUDFLARE SECURITY ---

# تشخیص HTTPS از سمت کلودفلر یا Nginx
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# دامنه‌های مورد اعتماد برای CSRF (هم آی‌پی هم دامنه)
CSRF_TRUSTED_ORIGINS = [
    'https://smartcopytraders.com',
    'https://www.smartcopytraders.com',
    'http://91.107.154.232',
    'https://91.107.154.232'
]

# فعلاً False برای جلوگیری از خطای Redirect تا قبل از ست شدن کامل SSL
SECURE_SSL_REDIRECT = False 
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# تنظیمات ضروری امنیتی
SESSION_COOKIE_HTTPONLY = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'