from actions.alert import AlertServiceExtended
from rest_framework import serializers

from .models import AlertCounter, AlertState


class AlertStateSerializer(serializers.ModelSerializer):
    """ Global Alert State serializer

        only 'current' field is allowed to be patched
    """

    class Meta:
        model = AlertState
        fields = '__all__'
        read_only_fields = ('id', 'name', 'info', 'order', 'increment')

    def update(self, instance, validated_data):
        """ set state current """
        with AlertServiceExtended() as service:
            if not self.context.get('by_counter'):
                # alert changed by name, counter should be reset to lower threshold
                data = service.reset_counter_to_threshold(instance)
                serializer = AlertCounterSerializer(data=data,
                                                    context={"by_state": True})
                if serializer.is_valid():
                    serializer.save()
            instance = service.set_state_current(instance)
            return instance


class AlertCounterSerializer(serializers.ModelSerializer):
    """ Global alert value counter """

    class Meta:
        model = AlertCounter
        fields = '__all__'

    def create(self, validated_data):
        alert_value = validated_data.get('value')
        comment = validated_data.get('comment', 'value changed by API')

        if not self.context.get('by_state'):
            try:
                with AlertServiceExtended() as service:
                    new_state = service.get_state_by_alert(alert_value)
                    # checking if base state is playable and can be switched
                    if new_state:
                        serializer = AlertStateSerializer(instance=new_state,
                                                          data={'current': True},
                                                          context={'by_counter': True})
                        if serializer.is_valid():
                            serializer.save()
            except Exception as e:
                raise serializers.ValidationError(f"exception occured when save {alert_value}:\n{e}")

        instance = AlertCounter.objects.create(value=alert_value,
                                               comment=comment)
        return instance
