from core.views import DynamicAuthMixin
from django_filters.rest_framework import DjangoFilterBackend
from eventlog import serializers
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from transport.interfaces import send_log, send_websocket

from .models import EventLog


class EventLogViewSet(viewsets.ModelViewSet, DynamicAuthMixin):
    """ Events in database """
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