from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import MenuViewSet

app_name = "behavior"

router = SimpleRouter()
router.register("menu", MenuViewSet)

urlpatterns = [path("", include(router.urls))]
