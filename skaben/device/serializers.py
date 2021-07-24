from rest_framework import serializers
from transport.interfaces import send_message_over_mqtt

from .models import Lock, Terminal
from shape.serializers import WorkModeSerializer


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
        """Отправляем конфиг клиенту.

           Эта логика находится здесь потому,
           что отправлять конфиг нужно не на каждом сохранении модели в админке,
           а на сохранении модели через API
        """
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
    mode_list = serializers.SerializerMethodField()
    mode_switch = serializers.SerializerMethodField()
    file_list = serializers.SerializerMethodField()

    class Meta:
        model = Terminal
        exclude = ('modes_normal', 'modes_extended')
        read_only_fields = ('id', 'uid', 'timestamp', 'alert')

    def get_mode_switch(self, obj):
        result = {}
        for mode in obj.modes():
            serialized = WorkModeSerializer(mode, context=self.context)
            data = serialized.data
            print(mode)
            for state in data.get("state", []):
                if not result.get(state):
                    result[state] = {
                        "extended": "",
                        "normal": ""
                    }
                if mode in obj.modes_extended.all():
                    result[state]["extended"] = mode.uuid
                if mode in obj.modes_normal.all():
                    result[state]["normal"] = mode.uuid
        return result

    def get_mode_list(self, obj):
        result = {}
        for mode in obj.modes():
            serialized = WorkModeSerializer(mode, context=self.context)
            result[str(mode.uuid)] = serialized.data
        return result

    def get_file_list(self, obj):
        """get full unique file list for all modes"""
        result = {}
        for mode in obj.modes():
            result.update(**mode.has_files)
        return result


class TerminalMQTTSerializer(DeviceSerializer):
    """ Terminal serializer """

    topic = 'terminal'
    file_list = serializers.ReadOnlyField()
    mode_list = serializers.ReadOnlyField()
    alert = serializers.ReadOnlyField()

    class Meta:
        model = Terminal
        exclude = ("id", "info", "override", "ip", "modes_normal", "modes_extended")
