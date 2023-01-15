from rest_framework import serializers
# from core.transport.interface import get_interface
from core.helpers import get_server_time, Hashable, get_hash_from
from skabenproto import CUP

from .models import Lock, Terminal
from content.serializers import WorkModeSerializer


class DeviceSerializer(serializers.ModelSerializer, Hashable):

    topic = ''
    alert = serializers.ReadOnlyField()

    class Meta:
        read_only_fields = ("alert",)

    def save(self):
        if self.context and self.context.get('no_send'):
            return super().save()
        # self.send_config(self)
        super().save()
    #
    # def send_config(self):
    #     """Отправляем конфиг клиенту.
    #
    #        Эта логика находится здесь потому,
    #        что отправлять конфиг нужно не на каждом сохранении модели в админке,
    #        а на сохранении модели через API
    #     """
    #     packet = CUP(
    #         topic=self.topic,
    #         uid=self.instance.uid,
    #         datahold=self.validated_data,
    #         config_hash=self.get_hash_from(self.validated_data),
    #         timestamp=get_server_time()
    #     )
    #     with get_interface() as mq:
    #         return mq.send_mqtt_skaben(packet)


class TerminalInternalSerializer(DeviceSerializer):
    """ Terminal serializer """

    topic = 'terminal'

    online = serializers.ReadOnlyField()

    class Meta:
        model = Terminal
        exclude = ('modes_normal', 'modes_extended')
        read_only_fields = ('id', 'uid', 'timestamp', 'alert')


class TerminalSerializer(TerminalInternalSerializer):
    """"""

    mode_list = serializers.SerializerMethodField()
    mode_switch = serializers.SerializerMethodField()
    file_list = serializers.SerializerMethodField()
    hash = serializers.SerializerMethodField()

    class Meta:
        model = Terminal
        exclude = ('id', 'ip', 'uid', 'modes_normal', 'modes_extended', 'info', 'override')

    def get_hash(self, obj):
        return get_hash_from({
            'alert': obj.alert,
            'hacked': obj.hacked,
            'blocked': obj.blocked,
            'powered': obj.powered,
            'mode_list': self.get_mode_list(obj),
        })

    def get_mode_switch(self, obj) -> dict:
        result = {}
        for mode in obj.modes():
            serialized = WorkModeSerializer(mode, context=self.context)
            data = serialized.data
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
