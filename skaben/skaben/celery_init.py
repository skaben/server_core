import os
import sys
from django.conf import settings

from celery import Celery

app = Celery('skaben')
app.config_from_object('django.conf:settings', namespace="CELERY")
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task():
    print('hello')
