from rest_framework import serializers

# from django.core.exceptions import ObjectDoesNotExist

from core.models import AlertState, AlertCounter


class AlertStateSerializer(serializers.ModelSerializer):
    """ Global Alert State serializer

        only 'current' field is allowed to be patched
    """

    class Meta:
        model = AlertState
        fields = '__all__'
        read_only_fields = ('id', 'name', 'descr')


# FIXME: move all logic to model method
"""
    # logic in viewset seems more readable and obvious
    alert_states = AlertState.objects.all()
    current_state = None
    other_states = None

    def _update_counter(self, instance):
        data = {'value': instance.threshold,
                'comment': f'changed from API to {instance.name}'}
        value = AlertCounterSerializer(data=data)
        value.is_valid()
        value.save()
        return value

    def update(self, instance, validated_data):
        name = validated_data.get('name')
        try:
            current_state = self.alert_states.get(current=True)
            if current_state.name == name:
                return f'state {name} is already active'
        except ObjectDoesNotExist:
            pass
        # TODO: exception handling
        try:
            other_states = self.alert_states.exclude(name=name)
            other_states.update(current=False)
        except ObjectDoesNotExist:
            pass
        instance.current = True
        instance.save()
        self._update_counter(instance)
        return instance
"""


class AlertCounterSerializer(serializers.ModelSerializer):
    """ Global alert value counter """

    class Meta:
        model = AlertCounter
        fields = '__all__'

    _ingame_states = AlertState.objects.filter(threshold__gt=0).all()


"""
    # fixme: move all logic to model method
    def create(self, validated_data):
        value = validated_data.get('value', -1)
        comment = validated_data.get('comment', 'value changed from API')
        if value not in range(0,1000):
            # fixme: raise serializer error
            return
        # checking if base state is playable and can be switched
        current_state = self._ingame_states.filter(current=True)
        if current_state:
            playable = dict()
            states = dict(enumerate(self._ingame_states))
            max_idx = len(self._ingame_states) - 1
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
                    pass
                    # new_state = states.get(index)
                    # state_serializer = AlertStateSerializer()
                    # state_serializer.update({'name': new_state.name})

        return AlertCounter.objects.create(value=value, comment=comment)
"""
