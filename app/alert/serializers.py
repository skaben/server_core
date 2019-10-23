from rest_framework import serializers

from core.models import AlertState


class AlertStateSerializer(serializers.ModelSerializer):
    """ Global Alert State serializer

        only 'current' field is allowed to be patched
    """

    class Meta:
        model = AlertState
        read_only_fields = ('id', 'name', 'descr')
        fields = '__all__'

    states = AlertState.objects.all()

    def update(self, instance, validated_data):
        name = validated_data.get('name')
        if not name:
            return 'bad request: missing name'
        new_state = self.states.filter(name=name).first()
        current_state = self.states.filter(current=True).first()
        if not new_state:
            return f'no such state: {name}'
        elif name == current_state.name:
            return f'{name} state already enabled'
        else:
            # set other states not current
            other = self.states.exclude(name=name)
            other.update(current=False)
            new_state.current = True
            new_state.save()
            # update values log
            value = serializers.AlertCounterSerializer()
            value.create({'value': new_state.threshold,
                          'comment': f'state changed to {new_state.name}'})
            value.save()
            return f'state changed to {name}'


"""
class AlertStateIdSerializer(serializers.HyperlinkedModelSerializer):

    id = serializers.ReadOnlyField()

    class Meta:
        model = AlertState
        fields = ('id',)

    def to_representation(self, obj):
        representation = super().to_representation(obj)
        return representation['id']


class AlertStateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AlertCounter
        fields = '__all__'

    # get all base states where threshold > 0
    states = AlertState.objects.filter(threshold__gt=0).all()

    def create(self, validated_data):
        value = validated_data.get('value', -1)
        comment = validated_data.get('comment', 'set by operator')
        if value not in range(0,1000):
            # raise error
            return
        # checking if base state is playable and can be switched
        current_state = self.states.filter(current=True)
        if current_state:
            playable = dict()
            _states = dict(enumerate(self.states))
            max_idx = len(self.states) - 1
            for index, st in _states.items():
                next_ = index + 1
                if next_ > max_idx:
                    next_threshold = 1000
                else:
                    next_threshold = _states[next_].threshold
                playable.update({index: (int(st.threshold),
                                         int(next_threshold))})
            for index, rng in playable.items():
                if value in range(*rng):
                    new_state = _states.get(index)
                    ssr = StateSerializer()
                    ssr.update({'name': new_state.name})

        return AlertCounter.objects.create(value=value, comment=comment)
"""
