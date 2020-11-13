from django.urls import path, include
from rest_framework.routers import SimpleRouter

from access import views

app_name = 'access'

router = SimpleRouter()
router.register('accesscode', views.AccessCodeViewSet)
router.register('permission', views.PermissionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
