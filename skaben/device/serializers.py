from rest_framework import serializers

from core.models import Lock, Terminal, Simple


class LockSerializer(serializers.ModelSerializer):
    """ Serializer for lock objects for sending over MQTT"""

    acl = serializers.ReadOnlyField()

    class Meta:
        model = Lock
        exclude = ['id', 'ip', 'override', 'info']
        read_only_fields = ('id',)


class LockHyperlinkedSerializer(serializers.ModelSerializer):
    """ Serializer for lock objects """

    online = serializers.ReadOnlyField()
    permissions = serializers.ReadOnlyField()

    class Meta:
        model = Lock
        fields = '__all__'
        read_only_fields = ('id',)


class TerminalSerializer(serializers.ModelSerializer):
    """ Serializer for terminal objects """

    class Meta:
        model = Terminal
        fields = '__all__'
        read_only_fields = ('id',)


class SimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Simple
        fields = '__all__'
        read_only_fields = ('id',)
