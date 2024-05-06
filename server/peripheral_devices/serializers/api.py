from peripheral_devices.models import LockDevice, TerminalDevice
from rest_framework import serializers


class DeviceSerializer(serializers.ModelSerializer):
    topic = serializers.ReadOnlyField()
    hash = serializers.SerializerMethodField()
    alert_state = serializers.ReadOnlyField()

    class Meta:
        read_only_fields = ("id", "mac_addr", "hash")

    @staticmethod
    def get_hash(obj):
        return obj.get_hash()


class LockSerializer(DeviceSerializer):
    """Lock serializer."""

    online = serializers.ReadOnlyField()
    acl = serializers.SerializerMethodField()

    @staticmethod
    def get_acl(lock):
        return lock.permissions()

    @property
    def get_hash(self):
        watch_list = ["alert_state", "closed", "blocked", "sound", "acl"]
        return super()._hash(self, watch_list)

    class Meta:
        model = LockDevice
        fields = "__all__"
        read_only_fields = ("id", "mac_addr", "timestamp", "online", "acl")


class TerminalSerializer(DeviceSerializer):
    """Lock serializer."""

    class Meta:
        model = TerminalDevice
        fields = "__all__"
        read_only_fields = ("id", "mac_addr", "timestamp", "alert", "online")
