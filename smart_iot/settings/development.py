"""
Development settings for smart_iot project.
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    'iot-app',
]


# CORS settings for React frontend (Development)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]


# Development logging - more verbose
LOGGING['root']['level'] = 'DEBUG'
LOGGING['loggers']['monitoring']['level'] = 'DEBUG'


# Email backend for development (console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# Cache settings for development (dummy cache)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}


# Development database (can override if needed)
# DATABASES['default']['NAME'] = 'smart_iot_dev'
