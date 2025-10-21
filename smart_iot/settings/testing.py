"""
Testing settings for smart_iot project.
"""

from .base import *

# Test settings
DEBUG = True

ALLOWED_HOSTS = ['*']


# Use faster password hasher for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]


# Use in-memory SQLite for faster tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}


# Disable migrations for tests
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = DisableMigrations()


# Cache - dummy cache for testing
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}


# Celery - eager mode for testing
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True


# Email backend for testing
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'


# Logging - minimal for tests
LOGGING['root']['level'] = 'ERROR'
LOGGING['loggers']['django']['level'] = 'ERROR'
LOGGING['loggers']['monitoring']['level'] = 'ERROR'
