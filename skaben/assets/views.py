from actions.models import UserInput
from assets import serializers
from core.views import DynamicAuthMixin
from device.models import MenuItem, WorkMode
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .models import AudioFile, HackGame, ImageFile, TextFile, VideoFile


class UserInputViewSet(viewsets.ModelViewSet, DynamicAuthMixin):
    """ Manage locks in database """
    queryset = UserInput.objects.all()
    serializer_class = serializers.UserInputSerializer


class TextFileViewSet(viewsets.ModelViewSet, DynamicAuthMixin):
    """ Manage locks in database """
    queryset = TextFile.objects.all()
    serializer_class = serializers.TextFileSerializer


class ImageFileViewSet(viewsets.ModelViewSet, DynamicAuthMixin):
    """ Manage locks in database """
    queryset = ImageFile.objects.all()
    serializer_class = serializers.ImageFileSerializer


class AudioFileViewSet(viewsets.ModelViewSet, DynamicAuthMixin):
    """ Manage locks in database """
    queryset = AudioFile.objects.all()
    serializer_class = serializers.AudioFileSerializer


class VideoFileViewSet(viewsets.ModelViewSet, DynamicAuthMixin):
    """ Manage locks in database """
    queryset = VideoFile.objects.all()
    serializer_class = serializers.VideoFileSerializer


class MenuItemViewSet(viewsets.ModelViewSet, DynamicAuthMixin):
    """ Manage locks in database """
    queryset = MenuItem.objects.all()
    serializer_class = serializers.MenuItemSerializer


class WorkModeViewSet(viewsets.ModelViewSet, DynamicAuthMixin):
    """ Manage locks in database """
    queryset = WorkMode.objects.all()
    serializer_class = serializers.WorkModeSerializer


class HackGameViewSet(viewsets.ModelViewSet, DynamicAuthMixin):
    """ Manage locks in database """
    queryset = HackGame.objects.all()
    serializer_class = serializers.HackGameSerializer
