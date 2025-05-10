from .base import *

DEBUG = True
ALLOWED_HOSTS = get_env_list('DJANGO_ALLOWED_HOSTS', ['*'])

# Disable security settings for development
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

# Enable browsable API
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'].append(
    'rest_framework.renderers.BrowsableAPIRenderer'
)