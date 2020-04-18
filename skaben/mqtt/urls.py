from django.urls import path, include
from rest_framework.routers import SimpleRouter

from mqtt import views

app_name = 'mqtt'

router = SimpleRouter()
router.register('mqtt', views.MQTTMessageViewSet)

urlpatterns = [
    path('send/', views.send_message),
    path('prod/', views.start),
    path('status/', views.stop),
    path('cons/', views.current)
]
