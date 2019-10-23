from django.urls import path, include
from rest_framework.routers import DefaultRouter

from lock import views

app_name = 'lock'

router = DefaultRouter()
router.register('lock', views.LockViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
