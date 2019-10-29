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

    def _update_counter(self, instance):
        data = {'value': instance.threshold,
                'comment': f'changed to {instance.name} by API call'}
        serializer = AlertCounterSerializer(data=data,
                                            context={'by_state': True})
        if serializer.is_valid():
            serializer.save()
            # fixme: error handling

    def update(self, instance, validated_data):
        current = validated_data.get('current')
        try:
            if instance.current:
                # print(f'state {name} is already active')
                return instance
            else:
                AlertState.objects.filter(current=True).update(current=False)
        except ObjectDoesNotExist:
            pass
        instance.current = current
        instance.save()
        qs = AlertState.objects.all()
        for x in qs:
            print(x.__dict__)
        # avoid second update of counter
        if not self.context.get('by_counter'):
            self._update_counter(instance)
        return instance


class AlertCounterSerializer(serializers.ModelSerializer):
    """ Global alert value counter """

    class Meta:
        model = AlertCounter
        fields = '__all__'

    _ingame = AlertState.objects.filter(threshold__gt=0).all()

    def _check_state_threshold(self, alert_value):
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
                state = states.get(index)
                s = AlertStateSerializer(instance=state,
                                         data={'current': True},
                                         context={'by_counter': True})
                if s.is_valid():
                    s.save()
                else:
                    raise serializers.ValidationError(s.errors)

    def create(self, validated_data):
        if self.context.get('by_state'):
            return super().create(validated_data)

        alert_value = validated_data.get('value', -1)
        comment = validated_data.get('comment', 'value changed by API')
        if alert_value not in range(1001):
            raise serializers.ValidationError('counter new value not in range')

        # checking if base state is playable and can be switched
        try:
            state_instance = self._ingame.filter(current=True)
            if state_instance:
                self._check_state_threshold(alert_value)
        except ObjectDoesNotExist:
            pass
            # f'current state is not ingame state:\n{self._ingame}'
            # raise serializers.ValidationError(err)

        counter = AlertCounter.objects.create(value=alert_value,
                                              comment=comment)
        return counter
