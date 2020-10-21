from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import MenuItem, WorkMode
from menu_item import serializers


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
