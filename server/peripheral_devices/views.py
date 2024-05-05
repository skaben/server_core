from core.views import DynamicAuthMixin
from peripheral_devices import serializers
from peripheral_devices.models import LockDevice, TerminalDevice
from rest_framework import viewsets


class LockViewSet(viewsets.ModelViewSet, DynamicAuthMixin):
    """Manage locks in database"""

    queryset = LockDevice.objects.all()
    serializer_class = serializers.LockSerializer


class TerminalViewSet(viewsets.ModelViewSet, DynamicAuthMixin):
    """Manage terminals in database"""

    queryset = TerminalDevice.objects.all()
    serializer_class = serializers.TerminalSerializer
