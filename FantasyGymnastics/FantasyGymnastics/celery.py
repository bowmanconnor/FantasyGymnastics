import os
from celery import Celery
import socket

if 'django' in socket.gethostname():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FantasyGymnastics.settings.production')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FantasyGymnastics.settings.development')

app = Celery('FantasyGymnastics')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
