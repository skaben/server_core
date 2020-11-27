from django.urls import path
from rest_framework.routers import SimpleRouter

from transport import views

app_name = 'transport'

router = SimpleRouter()
router.register('transport', views.MQTTMessageViewSet)

urlpatterns = [
    path('send/', views.send),
    path('start/', views.start),
    path('stop/', views.stop),
    path('ping/', views.ping),
    path('status/', views.healthcheck)
]

# path('status/', views.stop),
# path('cons/', views.current)
# path('send/', views.send_message),
