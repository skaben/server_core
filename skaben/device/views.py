from actions.device import send_config_all
from core.views import DynamicAuthMixin
from device import serializers
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Lock, Terminal  # , SimpleLight


@api_view(http_method_names=['GET'])
def update_devices(request):
    """update all devices"""
    try:
        send_config_all()
        return Response('success')
    except Exception as e:
        return Response({'exception': f'{e}'},
                        status=status.HTTP_403_FORBIDDEN)


class LockViewSet(viewsets.ModelViewSet, DynamicAuthMixin):
    """ Manage locks in database """
    queryset = Lock.objects.all()
    serializer_class = serializers.LockSerializer


class TerminalViewSet(viewsets.ModelViewSet, DynamicAuthMixin):
    """ Manage terminals in database """
    queryset = Terminal.objects.all()
    serializer_class = serializers.TerminalSerializer
#
#
# class SimpleLightViewSet(viewsets.ModelViewSet):
#     """ Manage lesser devices in database """
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = (IsAuthenticated,)
#
#     queryset = SimpleLight.objects.all()
#     serializer_class = serializers.SimpleLightSerializer
