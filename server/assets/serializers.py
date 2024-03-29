from rest_framework import serializers

from assets.models import (
    AudioFile,
    HackGame,
    ImageFile,
    SkabenFile,
    TextFile,
    VideoFile,
    UserInput
)


class UserInputSerializer(serializers.ModelSerializer):
    """ Serializer for menu item objects """

    class Meta:
        model = UserInput
        exclude = ("uuid",)


class FileSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField('get_file_url')

    class Meta:
        model = SkabenFile
        abstract = True

    def get_file_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.file.path)


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