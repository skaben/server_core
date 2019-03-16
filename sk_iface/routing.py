from django.conf.urls import url
from .consumers import WebEventConsumer

websocket_urlpatterns = [
    url(r'^ws/', WebEventConsumer),
]