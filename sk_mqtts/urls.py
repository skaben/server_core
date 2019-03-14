# mqtt control via Channels

import sk_mqtts.views as views
from django.urls import path, include

urlpatterns = [
    path('send/', views.mqtt_send),
    path('start/', views.mqtt_start),
    path('stop/', views.mqtt_stop),
    path('test-rcv/', views.mqtt_to_event),  # for test purposes TODO: tests
]