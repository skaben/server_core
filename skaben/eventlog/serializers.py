from rest_framework import serializers

from .models import EventLog


class EventSerializer(serializers.ModelSerializer):
    """ Serializer for event objects """

    human_time = serializers.ReadOnlyField()

    class Meta:
        model = EventLog
        fields = '__all__'
        read_only_fields = ('id',)