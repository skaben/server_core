from access import views
from django.urls import include, path
from rest_framework.routers import SimpleRouter

app_name = 'access'

router = SimpleRouter()
router.register('accesscode', views.AccessCodeViewSet)
router.register('permission', views.PermissionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
