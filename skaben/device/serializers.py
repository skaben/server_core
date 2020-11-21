from rest_framework import serializers

from core.models import Lock, Terminal
from transport.interfaces import send_unicast_mqtt
from assets.serializers import WorkModeSerializer


class DeviceSerializer(serializers.ModelSerializer):

    def save(self):
        if self.context and self.context.get('no_send'):
            return super().save()
        send_unicast_mqtt(self.topic, self.instance.uid, 'CUP', self.validated_data)
        super().save()


class LockSerializer(DeviceSerializer):
    """ Lock serializer for internal ops and MQTT """

    topic = 'lock'

    acl = serializers.ReadOnlyField()

    class Meta:
        model = Lock
        exclude = ('ip', 'override', 'info')
        read_only_fields = ("id", 'uid', 'online', 'acl', "timestamp")


class TerminalSerializer(DeviceSerializer):
    """ Terminal serializer """

    topic = 'terminal'

    modes_normal = serializers.HyperlinkedIdentityField(view_name="api:workmode-detail", many=True)
    modes_extended = serializers.HyperlinkedIdentityField(view_name="api:workmode-detail", many=True)

    class Meta:
        model = Terminal
        exclude = ("id", "info", "override", "ip", 'uid')
        read_only_fields = ('id', 'online', "timestamp", "modes_normal", "modes_extended")


class TerminalMQTTSerializer(DeviceSerializer):
    """ Terminal serializer """

    topic = 'terminal'
    file_list = serializers.ReadOnlyField()
    mode_list = serializers.ReadOnlyField()

    class Meta:
        model = Terminal
        exclude = ("id", "info", "override", "ip", "modes_normal", "modes_extended")

#
# class SimpleLightSerializer(DeviceSerializer):
#
#     topic = 'rgb'
#
#     class Meta:
#         model = SimpleLight
#         fields = ('online', 'config', 'timestamp')
