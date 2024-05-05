from peripheral_devices.models import LockDevice, TerminalDevice
from rest_framework import serializers


class DeviceSerializer(serializers.ModelSerializer):
    topic = serializers.ReadOnlyField()
    hash = serializers.ReadOnlyField()
    alert = serializers.ReadOnlyField()

    class Meta:
        read_only_fields = ("id", "mac_addr")


class LockSerializer(DeviceSerializer):
    """Lock serializer."""

    online = serializers.ReadOnlyField()
    acl = serializers.SerializerMethodField()

    @staticmethod
    def get_acl(lock):
        return lock.acl

    class Meta:
        model = LockDevice
        fields = "__all__"
        read_only_fields = ("id", "mac_addr", "timestamp", "acl", "online")


class TerminalSerializer(DeviceSerializer):
    """Lock serializer."""

    topic = "terminal"

    online = serializers.ReadOnlyField()
    acl = serializers.SerializerMethodField()
    hash = serializers.SerializerMethodField()

    @staticmethod
    def get_acl(lock):
        return lock.acl

    #
    # @property
    # def get_hash(self):
    #     watch_list = ["alert", "closed", "blocked", "sound", "acl"]
    #     return super()._hash(watch_list)

    class Meta:
        model = TerminalDevice
        fields = "__all__"
        read_only_fields = ("id", "mac_addr", "timestamp", "alert", "acl", "online")
