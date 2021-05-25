from rest_framework import serializers
from transport.interfaces import send_message_over_mqtt

from .models import Lock, Terminal


class DeviceSerializer(serializers.ModelSerializer):

    alert = serializers.ReadOnlyField()

    class Meta:
        read_only_fields = ("alert",)

    def save(self):
        if self.context and self.context.get('no_send'):
            return super().save()
        self.send_config()
        super().save()

    def send_config(self):
        return send_message_over_mqtt(self.topic, self.instance.uid, 'CUP', self.validated_data)


class LockSerializer(DeviceSerializer):
    """ Lock serializer for internal ops and MQTT """

    topic = 'lock'

    acl = serializers.ReadOnlyField()
    online = serializers.ReadOnlyField()

    class Meta:
        model = Lock
        fields = '__all__'
        read_only_fields = ("id", "uid", "timestamp", "alert", "acl", "online")


class LockMQTTSerializer(DeviceSerializer):
    """ Lock serializer for internal ops and MQTT """

    topic = 'lock'

    acl = serializers.ReadOnlyField()

    class Meta:
        model = Lock
        exclude = ('id', 'online')
        read_only_fields = ("id", "uid", "timestamp", "alert", "acl")


class TerminalSerializer(DeviceSerializer):
    """ Terminal serializer """

    topic = 'terminal'

    online = serializers.ReadOnlyField()

    modes_normal = serializers.HyperlinkedIdentityField(view_name="api:workmode-detail", many=True)
    modes_extended = serializers.HyperlinkedIdentityField(view_name="api:workmode-detail", many=True)

    class Meta:
        model = Terminal
        fields = '__all__'
        read_only_fields = ('id', 'uid', 'timestamp', 'modes_normal', 'modes_extended', 'alert')


class TerminalMQTTSerializer(DeviceSerializer):
    """ Terminal serializer """

    topic = 'terminal'
    file_list = serializers.ReadOnlyField()
    mode_list = serializers.ReadOnlyField()
    alert = serializers.ReadOnlyField()

    class Meta:
        model = Terminal
        exclude = ("id", "info", "override", "ip", "modes_normal", "modes_extended")
