from django.urls import path, include
from rest_framework.routers import SimpleRouter

from eventlog import views

app_name = 'eventlog'

router = SimpleRouter()
router.register('eventlog', views.EventLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
