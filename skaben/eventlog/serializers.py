from rest_framework import serializers

from core.models import EventLog


class EventLogSerializer(serializers.ModelSerializer):
    """ Serializer for lock objects """

    acl = serializers.ReadOnlyField()

    class Meta:
        model = EventLog
        fields = '__all__'
        read_only_fields = ('id',)
