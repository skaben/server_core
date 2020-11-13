from collections import OrderedDict
from rest_framework import serializers

from core.models import MenuItem, WorkMode, HackGame, UserInput, \
                        AudioFile, VideoFile, TextFile, ImageFile


class UserInputSerializer(serializers.ModelSerializer):
    """ Serializer for menu item objects """

    class Meta:
        model = UserInput
        exclude = ("id", "name",)


class AudioFileSerializer(serializers.ModelSerializer):

    class Meta:
        model = AudioFile
        exclude = ("id", "name",)


class VideoFileSerializer(serializers.ModelSerializer):

    class Meta:
        model = VideoFile
        exclude = ("id", "name",)


class ImageFileSerializer(serializers.ModelSerializer):

    class Meta:
        model = ImageFile
        exclude = ("id", "name",)


class TextFileSerializer(serializers.ModelSerializer):

    class Meta:
        model = TextFile
        exclude = ("id", "name",)


class HackGameSerializer(serializers.ModelSerializer):

    class Meta:
        model = HackGame
        exclude = ("id",)


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
        result = super().to_representation(instance)
        return OrderedDict([(key, result[key]) for key in result if result[key] is not None])


class WorkModeSerializer(serializers.ModelSerializer):

    menu_set = serializers.HyperlinkedIdentityField(view_name="api:menuitem-detail", many=True)

    class Meta:
        model = WorkMode
        exclude = ("id", "name")
