import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AgendamientoAulas.settings")

app = Celery("AgendamientoAulas")

# Lee settings CELERY_*
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()