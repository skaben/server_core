from events.models import EventRecord
from rest_framework import serializers


class EventSerializer(serializers.ModelSerializer):
    """ Serializer for event objects """

    human_time = serializers.ReadOnlyField()

    class Meta:
        model = EventRecord
        exclude = ('uuid',)
