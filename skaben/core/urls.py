from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework.routers import DefaultRouter

from access.urls import router as access_router
from alert.urls import router as alert_router
from assets.urls import router as assets_router
from eventlog.urls import router as eventlog_router
from device.urls import router as device_router
from transport.urls import router as transport_router

from core.views import CreateTokenView, login_view

# setting up nested router
core_router = DefaultRouter()

routers = [
    access_router,
    alert_router,
    eventlog_router,
    device_router,
    assets_router,
    transport_router,
]

for router in routers:
    core_router.registry.extend(router.registry)

urlpatterns = [
    path('auth/token/', CreateTokenView.as_view(), name='token'),
    path('auth/login/', login_view, name="login"),
    path('admin/', admin.site.urls),
    path('api/', include((core_router.urls, "core"), namespace="api")),
    path('transport/', include('transport.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
