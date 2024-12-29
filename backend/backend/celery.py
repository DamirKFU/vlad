import os

import celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
app = celery.Celery("backend")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
