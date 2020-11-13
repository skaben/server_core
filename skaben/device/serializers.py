from rest_framework import serializers

from core.models import Lock, Terminal
from transport.interfaces import send_unicast_mqtt
from access.serializers import PermissionsSerializer


class DeviceSerializer(serializers.ModelSerializer):

    def save(self):
        if self.context and self.context.get('send_config'):
            send_unicast_mqtt(self.topic, self.instance.uid, 'CUP', self.validated_data)
        super().save()


class LockSerializer(DeviceSerializer):
    """ Lock serializer for internal ops and MQTT """

    topic = 'lock'
    acl = serializers.ReadOnlyField()

    class Meta:
        model = Lock
        exclude = ['id', 'ip', 'override', 'info']
        read_only_fields = ('id',)


class LockHyperlinkedSerializer(DeviceSerializer):
    """ Lock serializer for DRF web API """

    topic = 'lock'
    online = serializers.ReadOnlyField()
    acl = serializers.ReadOnlyField()

    class Meta:
        model = Lock
        fields = '__all__'
        read_only_fields = ('id', 'online', 'acl')


class TerminalSerializer(DeviceSerializer):
    """ Terminal serializer """

    topic = 'terminal'
    file_list = serializers.ReadOnlyField()

    class Meta:
        model = Terminal
        fields = '__all__'
        read_only_fields = ('id',)

#
# class SimpleLightSerializer(DeviceSerializer):
#
#     topic = 'rgb'
#
#     class Meta:
#         model = SimpleLight
#         fields = ('online', 'config', 'timestamp')
