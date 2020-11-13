from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import MenuItem, WorkMode, HackGame, UserInput,\
                        TextFile, ImageFile, AudioFile, VideoFile
from assets import serializers


class UserInputViewSet(viewsets.ModelViewSet):
    """ Manage locks in database """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    queryset = UserInput.objects.all()
    serializer_class = serializers.UserInputSerializer


class TextFileViewSet(viewsets.ModelViewSet):
    """ Manage locks in database """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    queryset = TextFile.objects.all()
    serializer_class = serializers.TextFileSerializer


class ImageFileViewSet(viewsets.ModelViewSet):
    """ Manage locks in database """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    queryset = ImageFile.objects.all()
    serializer_class = serializers.ImageFileSerializer


class AudioFileViewSet(viewsets.ModelViewSet):
    """ Manage locks in database """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    queryset = AudioFile.objects.all()
    serializer_class = serializers.AudioFileSerializer


class VideoFileViewSet(viewsets.ModelViewSet):
    """ Manage locks in database """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    queryset = VideoFile.objects.all()
    serializer_class = serializers.VideoFileSerializer


class MenuItemViewSet(viewsets.ModelViewSet):
    """ Manage locks in database """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    queryset = MenuItem.objects.all()
    serializer_class = serializers.MenuItemSerializer


class WorkModeViewSet(viewsets.ModelViewSet):
    """ Manage locks in database """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    queryset = WorkMode.objects.all()
    serializer_class = serializers.WorkModeSerializer


class HackGameViewSet(viewsets.ModelViewSet):
    """ Manage locks in database """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    queryset = HackGame.objects.all()
    serializer_class = serializers.HackGameSerializer
