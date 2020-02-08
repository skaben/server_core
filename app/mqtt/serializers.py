from rest_framework import serializers

from core.models import MQTTMessage


class MQTTMessageSerializer(serializers.ModelSerializer):
    """ Serializer for menu item objects """

    class Meta:
        model = MQTTMessage
        fields = '__all__'
        read_only_fields = ('id',)
