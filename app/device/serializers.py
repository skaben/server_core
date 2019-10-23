from rest_framework import serializers

from core.models import Lock, Terminal, Tamed


class LockSerializer(serializers.ModelSerializer):
    """ Serializer for lock objects """

    acl = serializers.ReadOnlyField()

    class Meta:
        model = Lock
        fields = '__all__'
        read_only_fields = ('id',)
        # view_name = 'api:lock-detail'


class TerminalSerializer(serializers.ModelSerializer):
    """ Serializer for terminal objects """

    class Meta:
        model = Terminal
        fields = '__all__'
        read_only_fields = ('id',)
        # view_name = 'api:lock-detail'


class TamedSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tamed
        fields = '__all__'
        read_only_fields = ('id',)
