from django.conf.urls import url
from channels.routing import ProtocolTypeRouter, ChannelNameRouter
from mqtts.consumers import MQTTConsumer

application = ProtocolTypeRouter({
    # Empty for now (http->django views is added by default)
    "channel": ChannelNameRouter({
        "mqtt_send": MQTTConsumer,
        "app_control": MQTTConsumer,
    }),
})
