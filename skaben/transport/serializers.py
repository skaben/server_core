from core.models import MQTTMessage
from rest_framework import serializers


class MQTTMessageSerializer(serializers.ModelSerializer):
    """ Serializer for menu item objects """

    class Meta:
        model = MQTTMessage
        fields = '__all__'
        read_only_fields = ('id',)
