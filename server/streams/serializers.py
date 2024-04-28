from streams.models import StreamRecord
from rest_framework import serializers


class StreamRecordSerializer(serializers.ModelSerializer):
    """Serializer for event objects"""

    human_time = serializers.ReadOnlyField()

    class Meta:
        model = StreamRecord
        exclude = ("uuid",)
