from actions.serializers import UserInputSerializer
from assets.serializers import (AudioFileSerializer, HackGameSerializer,
                                ImageFileSerializer, TextFileSerializer,
                                VideoFileSerializer)
from rest_framework import serializers

from .models import AccessCode, MenuItem, Permission, WorkMode


class AccessCodeSerializer(serializers.ModelSerializer):
    """ Serializer for access code objects """

    class Meta:
        model = AccessCode
        fields = '__all__'
        read_only_fields = ('id',)


class PermissionSerializer(serializers.ModelSerializer):
    """ Serializer for lock-card relation objects """

    card = serializers.HyperlinkedIdentityField(view_name="api:accesscode-detail")
    lock = serializers.HyperlinkedIdentityField(view_name="api:lock-detail")
    state_id = serializers.HyperlinkedIdentityField(view_name="api:alertstate-detail", many=True)

    class Meta:
        model = Permission
        fields = "__all__"


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