import logging
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer

from sk_iface.models import *


class StateSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = State
        fields = '__all__'

    states = State.objects.all()

    def update(self, validated_data):
        name = validated_data.get('name')
        if not name:
            return 'bad request'
        new_state = self.states.filter(name=name).first()
        current_state = self.states.filter(current=True).first()
        if not new_state:
            return 'no such state'
        elif name == current_state.name:
            return f'{name} state already enabled'
        else:
            other = self.states.exclude(name=name)
            other.update(current=False)
            new_state.current = True
            new_state.save()
            # update values log
            value = ValueSerializer()
            value.create({'value': new_state.threshold,
                          'comment': f'state changed to {new_state.name}'})
            value.save()
            return f'state changed to {name}'


class StateIdSerializer(serializers.HyperlinkedModelSerializer):

    id = serializers.ReadOnlyField()

    class Meta:
        model = State
        fields = ('id',)

    def to_representation(self, obj):
        representation = super().to_representation(obj)
        return representation['id']


class ValueSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Value
        fields = '__all__'

    # get all base states where threshold > 0
    states = State.objects.filter(threshold__gt=0).all()

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

        return Value.objects.create(value=value, comment=comment)


class InfoTextSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Text
        fields = '__all__'
        view_name = 'api:text-detail'


class MenuItemSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MenuItem
        fields = '__all__'
        view_name = 'api:menu-detail'


class CardSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Card
        fields = '__all__'
        view_name = 'api:card-detail'


class PermissionSerializer(serializers.HyperlinkedModelSerializer):
    card = CardSerializer()
    state_id = StateIdSerializer(many=True)

    class Meta:
        model = Permission
        exclude = ('url', 'lock')
        view_name = 'api:permission'


class LockSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    acl_all = serializers.ReadOnlyField()

    class Meta:
        model = Lock
        fields = '__all__'
        view_name = 'api:lock-detail'


class TerminalSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Terminal
        fields = '__all__'
        view_name = 'api:terminal-detail'

