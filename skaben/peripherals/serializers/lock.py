from rest_framework import serializers
from .abstract import DeviceSerializer
from peripherals.models import LockDevice


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
