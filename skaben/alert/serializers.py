from rest_framework import serializers

from django.core.exceptions import ObjectDoesNotExist

from core.models import AlertState, AlertCounter
from alert.policies import PolicyManager


class AlertStateSerializer(serializers.ModelSerializer):
    """ Global Alert State serializer

        only 'current' field is allowed to be patched
    """

    class Meta:
        model = AlertState
        fields = '__all__'
        read_only_fields = ('id', 'name', 'descr')

    def reset_counter_to_threshold(self, instance):
        data = {'value': instance.threshold,
                'comment': f'changed to {instance.name} by API call'}
        serializer = AlertCounterSerializer(data=data,
                                            context={"by_state": True})
        if serializer.is_valid():
            serializer.save()

    def update(self, instance, validated_data):
        current = validated_data.get('current')
        try:
            if instance.current:
                # print(f'state {name} is already active')
                return instance
            else:
                AlertState.objects.filter(current=True)\
                                  .update(current=False)
        except ObjectDoesNotExist:
            pass
        instance.current = current
        if not self.context.get('by_counter'):
            # alert changed by name, counter should be reset to lower threshold
            self.reset_counter_to_threshold(instance)

        instance.save()
        manager = PolicyManager()
        manager.apply(instance)

        return instance

#fixme: counter ranges seems invalid
class AlertCounterSerializer(serializers.ModelSerializer):
    """ Global alert value counter """

    class Meta:
        model = AlertCounter
        fields = '__all__'

    _min_val = 0
    _max_val = 1000

    def get_state_by_alert(self, alert_value: int):
        """ Update Alert state as current """
        state_ranges = dict()
        self._ingame = [state for state in AlertState.objects.all().order_by("threshold")
                        if state.threshold in range(self._min_val, self._max_val)]

        states = dict(enumerate(self._ingame))

        for index, item in states.items():
            next = states.get(index + 1)
            next_threshold = getattr(next, 'threshold', self._max_val)
            state_ranges.update({index: [item.threshold, next_threshold]})

        print(state_ranges)

        for index, _range in state_ranges.items():
            if alert_value in range(*_range):
                return states.get(index)

    def create(self, validated_data):
        alert_value = validated_data.get('value')
        if alert_value not in range(self._min_val, self._max_val):
            raise serializers.ValidationError(f"{alert_value} not in range {self._min_val}:{self._max_val - 1}")
        comment = validated_data.get('comment', 'value changed by API')
        instance = AlertCounter.objects.create(value=alert_value,
                                               comment=comment)

        if not self.context.get('by_state'):
            # checking if base state is playable and can be switched
            new_state = self.get_state_by_alert(alert_value)
            if new_state in self._ingame:
                serializer = AlertStateSerializer(instance=new_state,
                                                  data={'current': True},
                                                  context={'by_counter': True})
                if serializer.is_valid():
                    serializer.save()

        return instance