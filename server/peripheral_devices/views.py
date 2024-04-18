from core.views import DynamicAuthMixin
from peripheral_devices import serializers
from peripheral_devices.models import LockDevice, TerminalDevice
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(http_method_names=['GET'])
def update_devices(request):
    """update all devices"""
    try:
        # send_config_all()
        # send_config_to_simple()
        return Response('success')
    except Exception as e:
        return Response({'exception': f'{e}'},
                        status=status.HTTP_403_FORBIDDEN)


@api_view(http_method_names=["POST", "PUT", "PATCH"])
def save_device(data):
    return data
    # save_device_payload(data)


class LockViewSet(viewsets.ModelViewSet, DynamicAuthMixin):
    """ Manage locks in database """
    queryset = LockDevice.objects.all()
    serializer_class = serializers.LockSerializer


class TerminalViewSet(viewsets.ModelViewSet, DynamicAuthMixin):
    """ Manage terminals in database """
    queryset = TerminalDevice.objects.all()
    serializer_class = serializers.TerminalSerializer
