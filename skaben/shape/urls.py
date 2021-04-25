from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (AccessCodeViewSet, MenuItemViewSet, PermissionViewSet,
                    WorkModeViewSet)

app_name = 'shape'

router = SimpleRouter()
router.register('accesscode', AccessCodeViewSet)
router.register('permission', PermissionViewSet)
router.register('menuitem', MenuItemViewSet)
router.register('workmode', WorkModeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]