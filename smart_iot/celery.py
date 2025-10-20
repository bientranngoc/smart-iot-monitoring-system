import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_iot.settings')
app = Celery('smart_iot')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()