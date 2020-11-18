from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Lock, Terminal #, SimpleLight
from device import serializers


class LockViewSet(viewsets.ModelViewSet):
    """ Manage locks in database """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    queryset = Lock.objects.all()
    serializer_class = serializers.LockSerializer


class TerminalViewSet(viewsets.ModelViewSet):
    """ Manage terminals in database """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

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
