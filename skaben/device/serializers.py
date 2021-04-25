from rest_framework import serializers
from transport.interfaces import send_message_over_mqtt

from .models import Lock, MenuItem, Terminal, WorkMode


class MenuItemSerializer(serializers.ModelSerializer):
    """ Serializer for menu item objects """

    user = UserInputSerializer()
    game = HackGameSerializer()
    text = TextFileSerializer()
    image = ImageFileSerializer()
    audio = AudioFileSerializer()
    video = VideoFileSerializer()

    class Meta:
        model = MenuItem
        exclude = ("id", "option")

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        is_files = ('audio', 'text', 'video', 'image')
        result = representation
        for key in representation:
            if key in is_files:
                file_repr = representation.get(key)
                if file_repr:
                    result[key] = file_repr["hash"]
        return OrderedDict([(key, result[key]) for key in result if result[key] is not None])


class WorkModeSerializer(serializers.ModelSerializer):

    menu_set = MenuItemSerializer(many=True)

    class Meta:
        model = WorkMode
        exclude = ("id", "name",)


class DeviceSerializer(serializers.ModelSerializer):

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
        read_only_fields = ('id', 'online', 'timestamp', 'modes_normal', 'modes_extended', 'alert')


class TerminalMQTTSerializer(DeviceSerializer):
    """ Terminal serializer """

    topic = 'terminal'
    file_list = serializers.ReadOnlyField()
    mode_list = serializers.ReadOnlyField()
    alert = serializers.ReadOnlyField()

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
