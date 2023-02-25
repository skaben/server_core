from rest_framework import serializers
from core.helpers import get_hash_from
from peripheral_devices.models import LockDevice, TerminalDevice

__all__ = (
    'LockSerializer',
    'TerminalSerializer',
)


class DeviceSerializer(serializers.ModelSerializer):

    topic = ''
    alert_current = serializers.ReadOnlyField()

    class Meta:
        read_only_fields = ('id', 'mac_addr')

    @staticmethod
    def _hash(obj: object, attrs: list[str]) -> str:
        return get_hash_from({attr: getattr(obj, attr) for attr in attrs})

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


class LockSerializer(DeviceSerializer):
    """ Lock serializer."""

    topic = 'lock'

    online = serializers.ReadOnlyField()
    acl = serializers.SerializerMethodField()
    hash = serializers.SerializerMethodField()

    @staticmethod
    def get_acl(lock):
        return lock.acl

    @property
    def get_hash(self):
        watch_list = [
            'alert',
            'closed',
            'blocked',
            'sound',
            'acl'
        ]
        return super()._hash(self, watch_list)

    class Meta:
        model = LockDevice
        fields = '__all__'
        read_only_fields = ("id", "uid", "timestamp", "alert", "acl", "online")


class TerminalSerializer(DeviceSerializer):
    """ Lock serializer."""

    topic = 'terminal'

    online = serializers.ReadOnlyField()
    acl = serializers.SerializerMethodField()
    hash = serializers.SerializerMethodField()

    @staticmethod
    def get_acl(lock):
        return lock.acl

    @property
    def get_hash(self):
        watch_list = [
            'alert',
            'closed',
            'blocked',
            'sound',
            'acl'
        ]
        return super()._hash(self, watch_list)

    class Meta:
        model = TerminalDevice
        fields = '__all__'
        read_only_fields = ("id", "mac_addr", "timestamp", "alert", "acl", "online")
