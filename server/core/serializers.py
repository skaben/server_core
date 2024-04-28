from rest_framework import serializers
from core.models.mqtt import DeviceTopic

__all__ = ["DeviceTopicSerializer"]


class DeviceTopicSerializer(serializers.Serializer):
    topics = serializers.ListField(child=serializers.CharField())

    def validate(self, attrs):
        if "topics" not in attrs or not isinstance(attrs["topics"], list):
            raise serializers.ValidationError("Invalid input. 'topics' field must be a list of strings.")
        bad_topics = [el for el in attrs["topics"] if el not in DeviceTopic.objects.get_topics_permitted()]
        if bad_topics:
            raise serializers.ValidationError(f"Invalid input. Topics is missing in SKABEN config: {bad_topics}")
        return attrs
