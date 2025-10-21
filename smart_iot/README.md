# smart_iot - Django Project Core

This directory contains the core Django project configuration and setup files for the Smart IoT Monitoring System.

## 📁 Directory Structure

```
smart_iot/
├── settings/             # Modular settings configuration
│   ├── __init__.py         # Auto-loads settings based on DJANGO_ENV
│   ├── base.py             # Common settings for all environments
│   ├── development.py      # Development-specific settings
│   ├── production.py       # Production-specific settings
│   ├── testing.py          # Testing-specific settings
│   └── README.md           # Settings documentation
├── __init__.py           
├── asgi.py               # ASGI configuration for async support
├── celery.py             # Celery configuration and app
├── urls.py               # Root URL configuration
├── wsgi.py               # WSGI configuration for deployment
└── README.md             
```

## 🎯 Purpose

This package contains the core configuration that ties together all Django apps and third-party integrations:

- **Settings Management**: Environment-specific configurations
- **URL Routing**: Root URL patterns and API endpoints
- **WSGI/ASGI**: Web server gateway interfaces
- **Celery**: Asynchronous task processing setup
- **Middleware**: Request/response processing pipeline

## 🔧 Configuration Files

### 1. `settings/` - Modular Settings

The settings are split into multiple files for better organization:

```python
# Automatically loads based on DJANGO_ENV environment variable
DJANGO_ENV=development  # Loads settings/development.py
DJANGO_ENV=production   # Loads settings/production.py
DJANGO_ENV=testing      # Loads settings/testing.py
```

**Features:**
- Environment-based configuration
- Secure secrets management via environment variables
- Optimized settings per environment
- Easy to add new environments (staging, qa, etc.)

See [settings/README.md](settings/README.md) for detailed documentation.

### 2. `celery.py` - Asynchronous Tasks

Configures Celery for background task processing:

```python
from celery import Celery

app = Celery('smart_iot')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

**Handles:**
- MQTT message processing
- Kafka stream consumption
- Sensor data aggregation
- Alert generation
- HVAC control automation
- Email notifications

**Configuration:**
```python
# In settings/base.py
CELERY_BROKER_URL = 'redis://iot-redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://iot-redis:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
```

### 3. `urls.py` - URL Routing

Root URL configuration that includes all app URLs:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('monitoring.urls')),
]
```

**API Structure:**
```
/admin/                          # Django admin interface
/api/buildings/                  # Building management
/api/zones/                      # Zone management
/api/zones/<id>/status/          # Real-time zone status
/api/building-alerts/            # Alert management
/api/hvac-controls/              # HVAC control
```

### 4. `wsgi.py` - WSGI Configuration

Web Server Gateway Interface for production deployment:

```python
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_iot.settings')
application = get_wsgi_application()
```

**Used by:**
- Gunicorn (recommended)
- uWSGI
- mod_wsgi (Apache)

**Production command:**
```bash
gunicorn smart_iot.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --timeout 60
```

### 5. `asgi.py` - ASGI Configuration

Asynchronous Server Gateway Interface for WebSocket support:

```python
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_iot.settings')
application = get_asgi_application()
```

**Future use cases:**
- WebSocket connections for real-time updates
- Server-Sent Events (SSE)
- HTTP/2 support
- Async views and middleware

## 🚀 Usage

### Starting the Project

#### Development:
```bash
# Using Django development server
python manage.py runserver 0.0.0.0:8000

# With Docker
docker-compose up
```

#### Production:
```bash
# Set environment
export DJANGO_ENV=production
export SECRET_KEY=your-secret-key

# Collect static files
python manage.py collectstatic --noinput

# Run with Gunicorn
gunicorn smart_iot.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4
```

### Celery Workers

Start Celery worker to process background tasks:

```bash
# Development
celery -A smart_iot worker -l info

# Production
celery -A smart_iot worker \
    -l warning \
    --concurrency=4 \
    --max-tasks-per-child=1000
```

Start Celery beat for periodic tasks:

```bash
celery -A smart_iot beat -l info
```

### Environment Variables

Required environment variables (set in `.env` or docker-compose):

```bash
# Django Core
DJANGO_ENV=development
SECRET_KEY=your-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
MYSQL_DATABASE=smart_iot
MYSQL_USER=user
MYSQL_PASSWORD=password
MYSQL_HOST=iot-mysql
MYSQL_PORT=3306

# Redis (Celery broker + cache)
REDIS_URL=redis://iot-redis:6379/0

# MongoDB (Time-series data)
MONGODB_URI=mongodb://root:root@iot-mongodb:27017/
MONGODB_DB_NAME=iot

# OpenSearch (Search & analytics)
OPENSEARCH_HOST=iot-opensearch:9200

# MQTT (IoT messaging)
MQTT_BROKER=iot-mosquitto
MQTT_PORT=1883
MQTT_TOPIC=sensors/data

# Kafka (Stream processing)
KAFKA_BOOTSTRAP_SERVERS=iot-kafka:9092
KAFKA_TOPIC=sensor-data

# MediaMTX (Video streaming)
MEDIAMTX_HOST=iot-mediamtx
MEDIAMTX_HTTP_PORT=8889
```

## 🔌 Integrated Services

### Database Backends

**MySQL** (Primary relational database)
- Buildings, zones, devices
- Sensors, cameras, HVAC controls
- Alerts, energy logs
- User authentication

**MongoDB** (Time-series data)
- Sensor readings
- Historical data
- Raw MQTT messages

**Redis** (Cache + message broker)
- Celery task queue
- Session storage (production)
- Real-time data cache

**OpenSearch** (Search & analytics)
- Full-text search
- Log aggregation
- Analytics and visualization

### Message Brokers

**MQTT** (IoT device communication)
- Lightweight messaging protocol
- Publish/Subscribe pattern
- Low bandwidth usage

**Kafka** (Stream processing)
- High-throughput messaging
- Data pipeline
- Real-time processing

### External Services

**MediaMTX** (Video streaming)
- RTSP → HLS conversion
- Live camera feeds
- Video recording

## 📊 Project Architecture

```
┌───────────────────────────────────────────────────┐
│                   smart_iot/                      │
│                 (Django Project)                  │
│                                                   │
│        ┌──────────────┐  ┌──────────────┐         │
│        │   settings/  │  │   celery.py  │         │
│        │              │  │              │         │
│        │ • base.py    │  │ • Worker     │         │
│        │ • dev.py     │  │ • Beat       │         │
│        │ • prod.py    │  │ • Tasks      │         │
│        └──────────────┘  └──────────────┘         │
│                                                   │
│        ┌──────────────┐  ┌──────────────┐         │
│        │    urls.py   │  │   wsgi.py    │         │
│        │              │  │              │         │
│        │ • /admin/    │  │ • Gunicorn   │         │
│        │ • /api/      │  │ • Production │         │
│        └──────────────┘  └──────────────┘         │
└───────────────────────────────────────────────────┘
            │                       │
            ▼                       ▼
    ┌──────────────┐        ┌──────────────┐
    │  monitoring/ │        │  Django Apps │
    │   (App)      │        │   (Future)   │
    └──────────────┘        └──────────────┘
```

## 🔐 Security Considerations

### Development
- DEBUG = True (detailed errors)
- Permissive CORS for frontend development
- Console email backend
- Weak SECRET_KEY (change for production)

### Production
- DEBUG = False
- HTTPS/SSL redirect
- Secure cookies (SESSION_COOKIE_SECURE, CSRF_COOKIE_SECURE)
- HSTS headers (1 year)
- Content type sniffing protection
- XSS filter
- Strong SECRET_KEY from environment
- ALLOWED_HOSTS validation
- CORS restricted to specific domains

### Best Practices

1. **Never commit secrets to git**
   ```bash
   # Use environment variables
   SECRET_KEY=os.getenv('SECRET_KEY')
   ```

2. **Use different SECRET_KEY per environment**
   ```bash
   # Generate new key
   python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
   ```

3. **Restrict ALLOWED_HOSTS in production**
   ```python
   ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
   ```

4. **Enable SSL/HTTPS in production**
   ```python
   SECURE_SSL_REDIRECT = True
   SESSION_COOKIE_SECURE = True
   CSRF_COOKIE_SECURE = True
   ```

## 🧪 Testing

### Run Tests

```bash
# All tests
export DJANGO_ENV=testing
python manage.py test

# Specific app
python manage.py test monitoring

# With coverage
coverage run --source='.' manage.py test
coverage report
```

### Test Settings

The `settings/testing.py` provides optimized test configuration:
- In-memory SQLite database
- Disabled migrations
- Fast password hasher
- Eager Celery tasks (synchronous)

## 📝 Management Commands

### Database Management

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Database shell
python manage.py dbshell
```

### Utility Commands

```bash
# Django shell
python manage.py shell

# Check for issues
python manage.py check

# Collect static files (production)
python manage.py collectstatic

# Clear cache
python manage.py clear_cache
```

## 🐛 Troubleshooting

### Settings not loading

```bash
# Check current environment
echo $DJANGO_ENV

# Verify settings module
python manage.py diffsettings
```

### Celery not processing tasks

```bash
# Check Celery worker
celery -A smart_iot inspect active

# Check Redis connection
redis-cli -h iot-redis ping

# Restart worker
docker restart iot-celery
```

### Import errors

```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Verify installed packages
pip list
```

### Database connection errors

```bash
# Test MySQL connection
python manage.py dbshell

# Check environment variables
env | grep MYSQL

# Restart database
docker restart iot-mysql
```

## 📚 Related Documentation

- [Settings Documentation](settings/README.md) - Detailed settings configuration
- [Main Project README](../README.md) - Overall project documentation
- [Monitoring App](../monitoring/README.md) - Smart Building app documentation
- [Django Documentation](https://docs.djangoproject.com/) - Official Django docs
- [Celery Documentation](https://docs.celeryproject.org/) - Celery task queue

## 🔄 Maintenance

### Regular Tasks

1. **Update dependencies**
   ```bash
   pip list --outdated
   pip install --upgrade package-name
   pip freeze > requirements.txt
   ```

2. **Database backups**
   ```bash
   python manage.py dumpdata > backup.json
   mysqldump -u user -p smart_iot > backup.sql
   ```

3. **Log rotation**
   ```bash
   # Logs are rotated automatically (see base.py)
   # maxBytes: 10MB, backupCount: 5
   ```

4. **Security updates**
   ```bash
   python manage.py check --deploy
   ```

## 🤝 Contributing

When modifying core project files:

1. **Settings changes**: Update appropriate settings file (base, dev, or prod)
2. **New URLs**: Add to `urls.py` with proper namespace
3. **Celery tasks**: Register in app's `tasks.py`
4. **Middleware**: Add to `settings/base.py` MIDDLEWARE list
5. **Documentation**: Update this README

## 📄 License

This project is part of the Smart IoT Monitoring System.
See main [LICENSE](../LICENSE) file for details.

---

**Maintained by:** Bien Tran Ngoc  
**Last Updated:** October 2025  
**Django Version:** 4.2.7  
**Python Version:** 3.11+
