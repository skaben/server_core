from core.views import DynamicAuthMixin
from rest_framework import status, viewsets

from .models import AccessCode, MenuItem, Permission, WorkMode, UserInput
from .serializers import (
    AccessCodeSerializer,
    MenuItemSerializer,
    PermissionSerializer,
    WorkModeSerializer,
    UserInputSerializer
)


class UserInputViewSet(viewsets.ModelViewSet, DynamicAuthMixin):
    """ Manage user input actions in database """
    queryset = UserInput.objects.all()
    serializer_class = UserInputSerializer


class AccessCodeViewSet(viewsets.ModelViewSet, DynamicAuthMixin):
    """ Events in database """
    queryset = AccessCode.objects.all()
    serializer_class = AccessCodeSerializer


class PermissionViewSet(viewsets.ModelViewSet, DynamicAuthMixin):
    """ Events in database """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer


class MenuItemViewSet(viewsets.ModelViewSet, DynamicAuthMixin):
    """ Manage locks in database """
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer


class WorkModeViewSet(viewsets.ModelViewSet, DynamicAuthMixin):
    """ Manage locks in database """
    queryset = WorkMode.objects.all()
    serializer_class = WorkModeSerializer
