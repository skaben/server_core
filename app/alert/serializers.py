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

    alert_states = AlertState.objects.all()

    def _update_counter(self, instance):
        data = {'value': instance.threshold,
                'comment': f'changed to {instance.name} by API call'}
        serializer = AlertCounterSerializer(data=data,
                                            context={'called_by_state': True})
        if serializer.is_valid():
            serializer.save()
            # fixme: error handling

    def update(self, instance, validated_data):
        name = validated_data.get('name')
        try:
            current_state = self.alert_states.get(current=True)
            if current_state.name == name:
                # (f'state {name} is already active')
                pass
        except ObjectDoesNotExist:
            pass
        instance.current = True
        instance.save()
        self._update_counter(instance)
        return instance


class AlertCounterSerializer(serializers.ModelSerializer):
    """ Global alert value counter """

    class Meta:
        model = AlertCounter
        fields = '__all__'

    _ingame = AlertState.objects.filter(threshold__gt=0).all()

    def _update_state(self, state_instance):
        """ Update Alert state as current """
        serializer = AlertStateSerializer(instance=state_instance,
                                          data={'current': True})
        if serializer.is_valid():
            serializer.save()
        else:
            raise serializer.ValidationError(serializer.errors)

    def create(self, validated_data):
        if self.context.get('called_by_state'):
            # avoid call to counter create from AlertState
            return super().create(validated_data)

        value = validated_data.get('value', -1)
        comment = validated_data.get('comment', 'value changed by API')
        if value not in range(1001):
            raise serializers.ValidationError('counter value not in range')

        counter = AlertCounter.objects.create(value=value, comment=comment)

        # checking if base state is playable and can be switched
        try:
            self._ingame.filter(current=True)
        except ObjectDoesNotExist:
            err = 'current state is not ingame state'
            raise serializers.ValidationError(err)

        playable = dict()
        states = dict(enumerate(self._ingame))
        max_idx = len(self._ingame) - 1
        # setting threshold ranges
        for index, st in states.items():
            _nxt = index + 1
            if _nxt > max_idx:
                next_threshold = 1000
            else:
                next_threshold = states[_nxt].threshold
            playable.update({index: (int(st.threshold),
                                     int(next_threshold))})
        for index, counter_range in playable.items():
            if value in range(*counter_range):
                state = states.get(index)
                if not state.current:
                    self._update_state(state)

        return counter
