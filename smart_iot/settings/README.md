# Settings Module

This directory contains Django settings split into multiple files for better organization and environment-specific configurations.

## Structure

```
settings/
├── __init__.py          # Auto-loads settings based on DJANGO_ENV
├── base.py              # Common settings for all environments
├── development.py       # Development-specific settings
├── production.py        # Production-specific settings
└── testing.py           # Testing-specific settings
```

## Usage

### Using DJANGO_ENV (Recommended)

Set the `DJANGO_ENV` environment variable to automatically load the appropriate settings:

```bash
# Development (default)
export DJANGO_ENV=development
python manage.py runserver

# Production
export DJANGO_ENV=production
gunicorn smart_iot.wsgi:application

# Testing
export DJANGO_ENV=testing
python manage.py test
```

### Using DJANGO_SETTINGS_MODULE (Alternative)

You can also specify the exact settings module:

```bash
export DJANGO_SETTINGS_MODULE=smart_iot.settings.production
python manage.py check
```

## Environment-Specific Settings

### Development (`development.py`)

- `DEBUG = True`
- Permissive CORS for local React development
- Console email backend
- Verbose logging
- Dummy cache

**Features:**
- Auto-reload on code changes
- Detailed error pages
- SQL query logging
- Development toolbar support (if installed)

### Production (`production.py`)

- `DEBUG = False`
- Strict security settings (SSL, HSTS, secure cookies)
- SMTP email backend
- Redis cache
- Error logging to files
- Static file optimization

**Security Features:**
- `SECURE_SSL_REDIRECT = True`
- `SESSION_COOKIE_SECURE = True`
- `CSRF_COOKIE_SECURE = True`
- `SECURE_HSTS_SECONDS = 31536000`

### Testing (`testing.py`)

- In-memory SQLite database
- Fast password hasher (MD5)
- Eager Celery tasks
- Disabled migrations
- Memory email backend
- Minimal logging

**Optimizations:**
- Faster test execution
- No database migrations
- Synchronous task execution

## Configuration Files

### base.py

Contains common settings used across all environments:

- Installed apps
- Middleware
- Templates
- Database configuration (MySQL)
- Password validators
- Internationalization
- Static files
- Third-party app settings:
  - Django REST Framework
  - Celery
  - OpenSearch
  - MongoDB
- Custom settings:
  - MQTT configuration
  - Kafka configuration
  - MediaMTX configuration

### Environment Variables

Required environment variables (set in `.env` file):

```bash
# Django
DJANGO_ENV=development
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
MYSQL_DATABASE=smart_iot
MYSQL_USER=user
MYSQL_PASSWORD=password
MYSQL_HOST=iot-mysql
MYSQL_PORT=3306

# Redis
REDIS_URL=redis://iot-redis:6379/0

# MongoDB
MONGODB_URI=mongodb://root:root@iot-mongodb:27017/
MONGODB_DB_NAME=iot

# OpenSearch
OPENSEARCH_HOST=iot-opensearch:9200

# MQTT
MQTT_BROKER=iot-mosquitto
MQTT_PORT=1883
MQTT_TOPIC=sensors/data

# Kafka
KAFKA_BOOTSTRAP_SERVERS=iot-kafka:9092
KAFKA_TOPIC=sensor-data

# MediaMTX
MEDIAMTX_HOST=iot-mediamtx
MEDIAMTX_HTTP_PORT=8889

# Production only
CORS_ALLOWED_ORIGINS=https://yourdomain.com
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-password
```

## Docker Configuration

In `docker-compose.yml`, set the environment:

```yaml
services:
  app:
    environment:
      - DJANGO_ENV=development
```

Or for production:

```yaml
services:
  app:
    environment:
      - DJANGO_ENV=production
      - SECRET_KEY=${SECRET_KEY}
```

## Migration from Old settings.py

The old `settings.py` has been backed up to `settings.py.backup`.

All existing functionality has been preserved and organized into:
- **base.py**: Core Django configuration
- **development.py**: Local development overrides
- **production.py**: Production security and performance settings
- **testing.py**: Test-specific optimizations

## Best Practices

1. **Never commit sensitive data**: Use environment variables for secrets
2. **Test in production mode locally**: Run with `DJANGO_ENV=production` before deploying
3. **Use different SECRET_KEY per environment**
4. **Keep base.py minimal**: Only common settings
5. **Document custom settings**: Add comments for custom configuration

## Troubleshooting

### Settings not loading

Check the `DJANGO_ENV` variable:
```bash
echo $DJANGO_ENV
```

### Import errors

Ensure all imports in `__init__.py` are correct:
```python
# In __init__.py
from .development import *  # or .production, .testing
```

### Database connection issues

Verify environment variables:
```bash
docker exec -it iot-app env | grep MYSQL
```

## Adding New Environments

To add a new environment (e.g., staging):

1. Create `staging.py`:
```python
from .base import *

DEBUG = False
ALLOWED_HOSTS = ['staging.example.com']
# ... staging-specific settings
```

2. Update `__init__.py`:
```python
elif env == 'staging':
    from .staging import *
```

3. Set environment variable:
```bash
export DJANGO_ENV=staging
```
