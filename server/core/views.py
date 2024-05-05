from django.conf import settings
from django.http import HttpResponse
import traceback

from core.helpers import format_routing_key
from core.transport.config import SkabenQueue
from core.transport.publish import get_interface
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, renderer_classes
from core.serializers import DeviceTopicSerializer
from core.models import DeviceTopic, DeviceTopicManager
from core.healthcheck import INTEGRATION_MODULE_MAP


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""

    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class DynamicAuthMixin:
    def get_authenticators(self, request, **kwargs):
        if settings.ENVIRONMENT in ("dev", "DEV"):
            return []
        return (TokenAuthentication,)

    def get_permissions(self, request, **kwargs):
        if settings.ENVIRONMENT in ("dev", "DEV"):
            return []
        return (IsAuthenticated,)


def login_view(request):
    html = """
    <html>
      <head>
        <title>SKABEN - Permission denied</title>
      </head>
      <body>
      Permission denied.
      </body>
    </html>
    """

    return HttpResponse(html)


class UpdateDeviceView(APIView):
    def post(self, request):
        """Update devices by provided topics."""
        try:
            serializer = DeviceTopicSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            _topics = serializer.data.get("topics", [])
            send_to = _topics[:]

            for special in DeviceTopicManager.special_topics:
                if special in _topics:
                    send_to.extend(DeviceTopic.objects.get_topics_by_type(special))
            result = set([topic for topic in send_to if topic not in DeviceTopicManager.special_topics])
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


@api_view(["GET"])
@renderer_classes((JSONRenderer,))
def health_check(request):
    result = {}
    for key, module in INTEGRATION_MODULE_MAP.items():
        integrity_check = module()
        integrity_check.run()
        messages = [msg.replace("\t", " ") for msg in integrity_check.messages]
        result[key] = {"ok": integrity_check.ok, "messages": messages, "errors": integrity_check.errors}
    return Response(result, status=status.HTTP_200_OK)
