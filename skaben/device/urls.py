from django.urls import path, include
from rest_framework.routers import SimpleRouter

from device import views

app_name = 'device'

router = SimpleRouter()
router.register('lock', views.LockViewSet)
router.register('terminal', views.TerminalViewSet)
router.register('tamed', views.TamedViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
