from celery import Celery

app = Celery('djangocelery')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()