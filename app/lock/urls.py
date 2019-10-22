from django.urls import path, include
from rest_framework.routers import DefaultRouter

from lock import views


router = DefaultRouter()
router.register('lock', views.LockViewSet)

app_name = 'lock'

urlpatterns = [
    path('', include(router.urls)),
]
