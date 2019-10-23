from django.urls import path, include
from rest_framework.routers import SimpleRouter

from alert import views

app_name = 'alert'

router = SimpleRouter()
router.register('alert_state', views.AlertStateViewSet)
# router.register('alert_counter', views.TerminalViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
