from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from django_filters.rest_framework import DjangoFilterBackend

from core.models import EventLog
from eventlog import serializers
from transport.interfaces import send_websocket, send_log


class EventLogViewSet(viewsets.ModelViewSet):
    """ Events in database """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    queryset = EventLog.objects.all()
    serializer_class = serializers.EventLogSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['level', 'access']

    def save(self):
        try:
            send_websocket(self.message, self.level, self.access)
        except Exception as e:
            send_log(f"when sending event via websocket: {e}", "error")
        super().save()