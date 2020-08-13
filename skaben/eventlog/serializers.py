from rest_framework import serializers

from core.models import EventLog


class EventLogSerializer(serializers.ModelSerializer):
    """ Serializer for event log objects """

    class Meta:
        model = EventLog
        fields = '__all__'
        read_only_fields = ('id',)

    def validate_message(self, data):
        if isinstance(data, dict):
            data = f"{data}"
        return data
