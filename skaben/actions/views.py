from core.views import DynamicAuthMixin
from rest_framework import viewsets

from .models import UserInput
from .serializers import ActionSerializer, UserInputSerializer


class UserInputViewSet(viewsets.ModelViewSet, DynamicAuthMixin):
    """ Manage locks in database """
    queryset = UserInput.objects.all()
    serializer_class = UserInputSerializer


class ActionViewSet(viewsets.ModelViewSet, DynamicAuthMixin):
    """ Manage locks in database """
    queryset = UserInput.objects.all()
    serializer_class = ActionSerializer