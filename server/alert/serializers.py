from alert.service import AlertService
from rest_framework import serializers

from alert.models import AlertCounter, AlertState


class AlertStateSerializer(serializers.ModelSerializer):
    """Global Alert State serializer

    only 'current' field is allowed to be patched
    """

    class Meta:
        model = AlertState
        fields = "__all__"
        read_only_fields = ("id", "name", "info", "order", "increment")

    def update(self, instance: AlertState, validated_data: dict) -> AlertState:
        """set state current"""
        with AlertService() as service:
            if not self.context.get("by_counter"):
                # alert changed by name, counter should be reset to lower threshold
                data = service.reset_counter(instance.threshold)
                serializer = AlertCounterSerializer(data=data, context={"by_state": True})
                if serializer.is_valid():
                    serializer.save()
            else:
                service.set_state_current(instance)
            return instance


class AlertCounterSerializer(serializers.ModelSerializer):
    """Global alert value counter"""

    class Meta:
        model = AlertCounter
        fields = "__all__"

    def create(self, validated_data: dict) -> AlertCounter:
        alert_value = validated_data.get("value")
        comment = validated_data.get("comment", "value changed by API")

        if not self.context.get("by_state"):
            try:
                with AlertService() as service:
                    new_state = service.get_state_by_alert(alert_value)
                    # checking if base state is playable and can be switched
                    if new_state:
                        serializer = AlertStateSerializer(
                            instance=new_state, data={"current": True}, context={"by_counter": True}
                        )
                        if serializer.is_valid():
                            serializer.save()
            except Exception as e:
                raise serializers.ValidationError(f"exception occured when save {alert_value}:\n{e}")

        instance = AlertCounter.objects.create(value=alert_value, comment=comment)
        return instance
