from rest_framework import serializers

from django.core.exceptions import ObjectDoesNotExist

from core.models import AlertState, AlertCounter


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
        return instance


class AlertCounterSerializer(serializers.ModelSerializer):
    """ Global alert value counter """

    class Meta:
        model = AlertCounter
        fields = '__all__'

    _ingame = AlertState.objects.filter(threshold__gt=0).all()
    _min_val = -5
    _max_val = 1000

    def get_state_by_alert(self, alert_value: int):
        """ Update Alert state as current """
        playable = dict()
        states = dict(enumerate(self._ingame))
        max_idx = len(self._ingame) - 1

        # setting threshold ranges
        for index, st in states.items():
            _nxt = index + 1
            next_threshold = 1000 if _nxt > max_idx else states[_nxt].threshold
            playable.update({index: (int(st.threshold),
                                     int(next_threshold))})

        for index, counter_range in playable.items():
            if alert_value in range(*counter_range):
                return states.get(index)

    def save(self):
        if not self.context.get('by_state'):
            alert_value = self.validated_data.get('value')
            if not alert_value:
                raise serializers.ValidationError(f'counter value missing')

            comment = self.validated_data.get('comment', 'value changed by API')
            if self._min_val > alert_value > self._max_val:
                raise serializers.ValidationError(f'counter new value not in range {self._min_val}:{self._max_val}')

            # checking if base state is playable and can be switched
            new_state = self.get_state_by_alert(alert_value)
            if new_state:
                serializer = AlertStateSerializer(instance=new_state,
                                                  data={'current': True},
                                                  context={'by_counter': True})
                if serializer.is_valid():
                    serializer.save()
            AlertCounter.objects.create(value=alert_value,
                                        comment=comment)

        return super().save()
