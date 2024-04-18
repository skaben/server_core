from alert.models import AlertCounter, AlertState
from alert.service import AlertService
from rest_framework import serializers


class AlertStateSerializer(serializers.ModelSerializer):
    """ Global Alert State serializer

        only 'current' field is allowed to be patched
    """

    class Meta:
        model = AlertState
        fields = '__all__'
        read_only_fields = ('id', 'name', 'info', 'order', 'increment')


class AlertCounterSerializer(serializers.ModelSerializer):
    """ Global alert value counter """

    class Meta:
        model = AlertCounter
        fields = '__all__'

    def create(self, validated_data: dict) -> AlertCounter:
        alert_value = validated_data.get('value')
        comment = validated_data.get('comment', 'value changed by API')
        instance = AlertCounter.objects.create(value=alert_value,
                                               comment=comment)
        return instance
