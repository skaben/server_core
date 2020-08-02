from rest_framework import serializers

from core.models import Lock, Terminal, Simple, SimpleLight
from transport.interfaces import send_unicast_mqtt


class DeviceSerializer(serializers.ModelSerializer):

    def save(self):
        if self.context and self.context.get('send_config'):
            send_unicast_mqtt(self.topic, self.instance.uid, 'CUP', self.validated_data)
        super().save()


class LockSerializer(DeviceSerializer):
    """ Serializer for lock objects for sending over MQTT"""

    topic = 'lock'
    acl = serializers.ReadOnlyField()

    class Meta:
        model = Lock
        exclude = ['id', 'ip', 'override', 'info']
        read_only_fields = ('id',)


class LockHyperlinkedSerializer(DeviceSerializer):
    """ Serializer for lock objects """

    topic = 'lock'
    online = serializers.ReadOnlyField()
    permissions = serializers.ReadOnlyField()

    class Meta:
        model = Lock
        fields = '__all__'
        read_only_fields = ('id',)


class TerminalSerializer(DeviceSerializer):
    """ Serializer for terminal objects """

    topic = 'terminal'

    class Meta:
        model = Terminal
        fields = '__all__'
        read_only_fields = ('id',)


class SimpleSerializer(DeviceSerializer):

    topic = 'simple'

    class Meta:
        model = Simple
        fields = '__all__'
        read_only_fields = ('id',)


class SimpleLightSerializer(DeviceSerializer):

    topic = 'rgb'

    class Meta:
        model = SimpleLight
        fields = ('online', 'config', 'timestamp')
