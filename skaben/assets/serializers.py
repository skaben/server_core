from collections import OrderedDict
from rest_framework import serializers

from core.models import MenuItem, WorkMode, HackGame, UserInput, \
                        AudioFile, VideoFile, TextFile, ImageFile, File


class UserInputSerializer(serializers.ModelSerializer):
    """ Serializer for menu item objects """

    class Meta:
        model = UserInput
        exclude = ("id", "name",)


class FileSerializer(serializers.ModelSerializer):

    file = serializers.SerializerMethodField('get_file_url')

    def get_file_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.file.path)

    class Meta:
        model = File
        abstract = True


class AudioFileSerializer(FileSerializer):

    class Meta:
        model = AudioFile
        exclude = ("id", )
        read_only_fields = ("hash", )


class VideoFileSerializer(FileSerializer):

    class Meta:
        model = VideoFile
        exclude = ("id",)
        read_only_fields = ("hash", )


class ImageFileSerializer(FileSerializer):

    class Meta:
        model = ImageFile
        exclude = ("id",)
        read_only_fields = ("hash", )


class TextFileSerializer(serializers.ModelSerializer):

    class Meta:
        model = TextFile
        fields = "__all__"


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