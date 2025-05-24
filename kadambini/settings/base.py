from pathlib import Path
import os
import sys
from dotenv import load_dotenv
from datetime import timedelta


BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / '.env')

def get_env_list(var, default=None):
    value = os.getenv(var)
    return value.split(',') if value else default or []

def get_bool(var, default=False):
    return os.getenv(var, str(default)).lower() in ('true', '1', 't')


SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
DEBUG = get_bool('DJANGO_DEBUG', False)
ALLOWED_HOSTS = get_env_list('DJANGO_ALLOWED_HOSTS', ['*'] if DEBUG else [])


INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party apps
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt.token_blacklist',

    # Local apps
    'basic_app',
    'authentication',
    'maintree',
    'analysis',
]

MIDDLEWARE = [
    # cors middleware
    'corsheaders.middleware.CorsMiddleware',

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, 'templates')],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

ROOT_URLCONF = 'kadambini.urls'
WSGI_APPLICATION = 'kadambini.wsgi.application'

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

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT=os.path.join(BASE_DIR,'staticfiles')
STATICFILES_DIRS=[os.path.join(BASE_DIR,'static')]
MEDIA_URL='/media/'
MEDIA_ROOT=os.path.join(BASE_DIR,'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'authentication.CustomUser'

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER_EMAIL')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_USER_PASSWORD')

# Security
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

# CORS
CORS_ALLOWED_ORIGINS = get_env_list('DJANGO_CORS_ALLOWED_ORIGINS')
CORS_ALLOW_CREDENTIALS = get_bool('DJANGO_CORS_ALLOW_CREDENTIALS')
CSRF_TRUSTED_ORIGINS = get_env_list('DJANGO_CSRF_TRUSTED_ORIGINS')

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
    ]
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'TOKEN_OBTAIN_SERIALIZER': 'authentication.serializers.CustomTokenObtainPairSerializer',
}

# Jazzmin
JAZZMIN_SETTINGS = {
    "site_title": "Arogya Kadambini",
    "site_header": "Arogya Kadambini Dashboard",
    "site_logo": "../static/assets/img/logo.png",
    "login_logo": "../static/assets/img/logo.png",
    "welcome_sign": "Welcome to Arogya Kadambini Admin Panel",
    "copyright": "Arogya Kadambini © 2024",
    "user_avatar": "profile.picture",
    "footer_links": [
        {"name": "Arogya Kadambini", "url": "https://arogyakadambini.in", "new_window": True},
        {"name": "Support", "url": "mailto:support@gmail.com", "new_window": True},
    ],
    "custom_css": "../static/assets/css/jazzmin.css",
    # "custom_js": "../static/assets/js/jazzmin.js",
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024*1024*5,  # 5MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'DEBUG' if DEBUG else 'INFO',
    },
}