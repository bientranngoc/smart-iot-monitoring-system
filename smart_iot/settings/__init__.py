"""
Django settings for smart_iot project.

This module automatically loads the appropriate settings based on the
DJANGO_SETTINGS_MODULE environment variable or DJANGO_ENV.

Default is 'development' settings.

Usage:
    - Development: export DJANGO_ENV=development (default)
    - Production: export DJANGO_ENV=production
    - Testing: export DJANGO_ENV=testing
    
Or set DJANGO_SETTINGS_MODULE directly:
    - export DJANGO_SETTINGS_MODULE=smart_iot.settings.production
"""

import os

# Determine which settings to use
env = os.getenv('DJANGO_ENV', 'development').lower()

if env == 'production':
    from .production import *
elif env == 'testing':
    from .testing import *
else:
    # Default to development
    from .development import *

print(f"🔧 Loaded settings: {env}")
