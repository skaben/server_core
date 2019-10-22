from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Lock
from lock import serializers


class LockViewSet(viewsets.ModelViewSet):
    """ Manage tags in database """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    queryset = Lock.objects.all()
    serializer_class = serializers.LockSerializer
