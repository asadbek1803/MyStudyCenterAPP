from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Django sozlamalarini o‘qing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

# Celery sozlamalarini o‘rnatish
app.config_from_object('django.conf:settings', namespace='CELERY')

# Django model va tasklarni avtomatik ro‘yxatga olish
app.autodiscover_tasks()