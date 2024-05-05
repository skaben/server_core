from alert.urls import router as alert_router
from assets.urls import router as assets_router
from core import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from peripheral_devices.urls import router as device_router
from rest_framework.routers import DefaultRouter
from streams.urls import router as stream_router

# setting up nested router
core_router = DefaultRouter()

routers = [alert_router, assets_router, stream_router, device_router]

for router in routers:
    core_router.registry.extend(router.registry)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include((core_router.urls, "core"), namespace="api")),
    path("api/auth/token/", views.CreateTokenView.as_view(), name="token"),
    path("api/auth/login/", views.login_view, name="login"),
    path("api/device/", include("peripheral_devices.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("ops/update-devices/", views.UpdateDeviceView.as_view(), name="update-devices"),
    path("ops/healthcheck/", views.health_check, name="healthcheck"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
