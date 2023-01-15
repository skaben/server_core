from core.helpers import Hashable
from rest_framework import serializers


class DeviceSerializer(serializers.ModelSerializer, Hashable):

    topic = ''
    alert_current = serializers.ReadOnlyField()

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

