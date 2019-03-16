from django.conf.urls import url
from channels.routing import ProtocolTypeRouter, ChannelNameRouter, URLRouter
import sk_iface.routing
from sk_mqtts.consumers import MQTTConsumer
from sk_iface.consumers import EventConsumer, WebEventConsumer

application = ProtocolTypeRouter({
    # Empty for now (http->django views is added by default)
    "channel": ChannelNameRouter({
        "mqtts": MQTTConsumer,
        "events": EventConsumer,
        "web": WebEventConsumer,
    }),
    "websocket": URLRouter(
        sk_iface.routing.websocket_urlpatterns
    )
})
