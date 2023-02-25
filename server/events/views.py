from core.views import DynamicAuthMixin
from django_filters.rest_framework import DjangoFilterBackend
from events import serializers
from rest_framework import viewsets, filters
from .models import EventRecord


class EventViewSet(viewsets.ModelViewSet, DynamicAuthMixin):
    """ Events in database """
    queryset = EventRecord.objects.all()
    serializer_class = serializers.EventSerializer

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['level', 'source', 'stream', 'message__type']
    ordering_fields = ['timestamp']
    ordering = ('timestamp',)
