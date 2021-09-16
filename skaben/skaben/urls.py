from alert.urls import router as alert_router
from actions.urls import router as actions_router
from assets.urls import router as assets_router
from core.views import CreateTokenView, login_view
from device.urls import router as device_router
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from eventlog.urls import router as eventlog_router
from rest_framework.routers import DefaultRouter
from shape.urls import router as shape_router
from transport.urls import router as transport_router

# setting up nested router
core_router = DefaultRouter()

routers = [
    alert_router,
    assets_router,
    eventlog_router,
    device_router,
    shape_router,
    transport_router,
    actions_router
]

for router in routers:
    core_router.registry.extend(router.registry)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include((core_router.urls, "core"), namespace="api")),
    path('api/auth/token/', CreateTokenView.as_view(), name='token'),
    path('api/auth/login/', login_view, name="login"),
    path('api/transport/', include('transport.urls')),
    path('api/device/', include('device.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)