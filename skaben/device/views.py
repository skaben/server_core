from actions.device import send_config_all, send_config_to_simple
from transport.interfaces import save_device_payload
from core.views import DynamicAuthMixin
from device import serializers
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Lock, Terminal


@api_view(http_method_names=['GET'])
def update_devices(request):
    """update all devices"""
    try:
        send_config_all()
        send_config_to_simple()
        return Response('success')
    except Exception as e:
        return Response({'exception': f'{e}'},
                        status=status.HTTP_403_FORBIDDEN)


@api_view(http_method_names=["POST", "PUT", "PATCH"])
def save_device(data):
    save_device_payload(data)


class LockViewSet(viewsets.ModelViewSet, DynamicAuthMixin):
    """ Manage locks in database """
    queryset = Lock.objects.all()
    serializer_class = serializers.LockSerializer


class TerminalInternalViewSet(viewsets.ModelViewSet, DynamicAuthMixin):
    """ Manage terminals in database """
    queryset = Terminal.objects.all()
    serializer_class = serializers.TerminalInternalSerializer


class TerminalViewSet(viewsets.ModelViewSet, DynamicAuthMixin):
    """ Manage terminals in database """
    queryset = Terminal.objects.all()
    serializer_class = serializers.TerminalSerializer
