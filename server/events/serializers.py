from rest_framework import serializers

from events.models import EventRecord


class EventSerializer(serializers.ModelSerializer):
    """ Serializer for event objects """

    human_time = serializers.ReadOnlyField()

    class Meta:
        model = EventRecord
        exclude = ('uuid',)
