from django.contrib import admin
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from access.urls import router as access_router
from alert.urls import router as alert_router
from eventlog.urls import router as eventlog_router
from device.urls import router as device_router
from menu_item.urls import router as menu_router
from transport.urls import router as transport_router

from core.views import CreateTokenView

# setting up nested router
core_router = DefaultRouter()

routers = [
    access_router,
    alert_router,
    eventlog_router,
    device_router,
    menu_router,
    transport_router,
]

for router in routers:
    core_router.registry.extend(router.registry)

urlpatterns = [
    path('auth/token/', CreateTokenView.as_view(), name='token'),
    path('admin/', admin.site.urls),
    path('api/', include(core_router.urls)),
    path('transport/', include('transport.urls'))
]
