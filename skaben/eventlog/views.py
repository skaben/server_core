from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import EventLog
from eventlog import serializers


class EventLogViewSet(viewsets.ModelViewSet):
    """ Events in database """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    queryset = EventLog.objects.all()
    serializer_class = serializers.EventLogSerializer
