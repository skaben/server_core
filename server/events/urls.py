from django.urls import include, path
from events import views
from rest_framework.routers import SimpleRouter

app_name = "events"

router = SimpleRouter()
router.register("events", views.EventViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
