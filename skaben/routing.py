import sk_iface.routing
from sk_mqtts.consumers import MQTTConsumer
from sk_iface.consumers import EventConsumer, WebEventConsumer
from channels.routing import ProtocolTypeRouter, ChannelNameRouter, URLRouter

application = ProtocolTypeRouter({
    # Empty for now (http->django views is added by default)
    "channel": ChannelNameRouter({
        "mqtts": MQTTConsumer,
        "events": EventConsumer,
    }),
    "websocket": URLRouter(
        sk_iface.routing.websocket_urlpatterns
    )
})
