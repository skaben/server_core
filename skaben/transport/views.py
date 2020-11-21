from rest_framework.decorators import api_view

from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import MQTTMessage
from core.views import DynamicAuthMixin
from core.tasks.main import run_workers, run_pinger, stop_all

from transport import serializers
from transport.interfaces import send_message_over_mqtt, send_log


@api_view(http_method_names=['GET'])
def start(request):
    try:
        workers = run_workers()
        return Response(workers)
    except Exception as e:
        return Response({'exception': f'{e}'},
                        status=status.HTTP_403_FORBIDDEN)


@api_view(http_method_names=['GET'])
def stop(request):
    try:
        results = stop_all()
        return Response(results)
    except Exception as e:
        return Response({'exception': f'{e}'},
                        status=status.HTTP_403_FORBIDDEN)


@api_view(http_method_names=['GET'])
def ping(request):
    try:
        pinger = run_pinger()
        return Response(pinger)
    except Exception as e:
        return Response({'exception': f'{e}'},
                        status=status.HTTP_403_FORBIDDEN)


@api_view(http_method_names=['POST'])
def send(request):
    try:
        topic = request.data.get('topic', '')
        uid = request.data.get('uid', '')
        command = request.data.get('command', '')
        payload = request.data.get('payload', {})
        result = send_message_over_mqtt(topic, uid, command, payload)
        return Response(result)
    except Exception as e:
        return Response({'exception': f'{e}'},
                        status=status.HTTP_403_FORBIDDEN)


class MQTTMessageViewSet(viewsets.ModelViewSet, DynamicAuthMixin):
    """ MQTT message all """
    queryset = MQTTMessage.objects.all()
    serializer_class = serializers.MQTTMessageSerializer
