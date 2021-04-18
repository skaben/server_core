from django.urls import include, path
from eventlog import views
from rest_framework.routers import SimpleRouter

app_name = 'eventlog'

router = SimpleRouter()
router.register('eventlog', views.EventLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
