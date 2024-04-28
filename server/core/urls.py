from alert.urls import router as alert_router
from assets.urls import router as assets_router
from core.views import CreateTokenView, health_check, login_view
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from streams.urls import router as stream_router
from peripheral_devices.urls import router as device_router
from rest_framework.routers import DefaultRouter

# setting up nested router
core_router = DefaultRouter()

routers = [
    alert_router,
    assets_router,
    stream_router,
    device_router,
]

for router in routers:
    core_router.registry.extend(router.registry)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include((core_router.urls, "core"), namespace="api")),
    path("api/auth/token/", CreateTokenView.as_view(), name="token"),
    path("api/auth/login/", login_view, name="login"),
    path("api/device/", include("peripheral_devices.urls")),
    path("healthcheck", health_check, name="healthcheck"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
