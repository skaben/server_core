"""skaben URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from menu_item.urls import router as menu_router
from device.urls import router as dev_router
from alert.urls import router as alert_router
from mqtt.urls import router as mqtt_router
from eventlog.urls import router as eventlog_router

# setting up nested router
api_router = DefaultRouter()
api_router.registry.extend(dev_router.registry)
api_router.registry.extend(menu_router.registry)
api_router.registry.extend(alert_router.registry)
api_router.registry.extend(mqtt_router.registry)
api_router.registry.extend(eventlog_router.registry)

urlpatterns = [
    path('', include('core.urls')),
    path('admin/', admin.site.urls),
    path('api/', include((api_router.urls, 'api'), namespace='api')),
    path('mqtt/', include('mqtt.urls'))
]
