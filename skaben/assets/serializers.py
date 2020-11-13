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
        fields = ("file",)


class VideoFileSerializer(serializers.ModelSerializer):

    class Meta:
        model = VideoFile
        fields = ("file",)


class ImageFileSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        result = super().to_representation(instance)
        return result

    class Meta:
        model = ImageFile
        fields = ("file",)


class TextFileSerializer(serializers.ModelSerializer):

    class Meta:
        model = TextFile
        fields = ("file",)


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

    menu_set = MenuItemSerializer(many=True)

    class Meta:
        model = WorkMode
        exclude = ("id", "name")
