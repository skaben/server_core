from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Lock, Terminal #, SimpleLight
from core.views import DynamicAuthMixin
from device import serializers


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
