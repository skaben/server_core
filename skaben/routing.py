from django.conf.urls import url
from channels.routing import ProtocolTypeRouter, ChannelNameRouter
from sk_mqtts.consumers import MQTTConsumer
from sk_iface.consumers import EventConsumer

application = ProtocolTypeRouter({
    # Empty for now (http->django views is added by default)
    "channel": ChannelNameRouter({
        "mqtts": MQTTConsumer,
        "events": EventConsumer,
    }),
})
