from django.urls import path
from channels.routing import ProtocolTypeRouter, ChannelNameRouter, URLRouter

from mqtt.consumers import MQTTConsumer
from core.consumers import EventConsumer, WebSocketConsumer


websocket_urlpatterns = [
    path(r'^ws/', WebSocketConsumer),
]

application = ProtocolTypeRouter({
    "channel": ChannelNameRouter({
        "mqtt": MQTTConsumer,
        "internal": EventConsumer,
    }),
    "websocket": URLRouter(websocket_urlpatterns)
})

