import traceback

from core.views import DynamicAuthMixin
from core.helpers import format_routing_key
from core.transport.config import SkabenQueue
from core.transport.packets import SkabenPacketTypes
from core.transport.publish import get_interface
from core.models.mqtt import DeviceTopic, DeviceTopicManager
from core.serializers import DeviceTopicSerializer
from peripheral_devices import serializers
from peripheral_devices.models import LockDevice, TerminalDevice
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response


class UpdateDeviceView(APIView):

    def post(self, request):
        """Update devices by provided topics."""
        try:
            serializer = DeviceTopicSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            _topics = serializer.data.get("topics", [])
            send_to = _topics[:]

            for special in DeviceTopicManager._special_topics:
                if special in _topics:
                    send_to.extend(DeviceTopic.objects.get_topics_by_type(special))
            result = set([topic for topic in send_to if topic not in DeviceTopicManager._special_topics])
            with get_interface() as publisher:
                for topic in result:
                    publisher.publish(
                        body={},
                        exchange=publisher.config.exchanges.get("internal"),
                        routing_key=format_routing_key(SkabenQueue.CLIENT_UPDATE.value, topic, "all"),
                    )
            return Response({"update_requested": _topics, "update_sent": result})
        except Exception as e:
            return Response(
                {"exception": f"{e} {traceback.format_exc()}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LockViewSet(viewsets.ModelViewSet, DynamicAuthMixin):
    """Manage locks in database"""

    queryset = LockDevice.objects.all()
    serializer_class = serializers.LockSerializer


class TerminalViewSet(viewsets.ModelViewSet, DynamicAuthMixin):
    """Manage terminals in database"""

    queryset = TerminalDevice.objects.all()
    serializer_class = serializers.TerminalSerializer
