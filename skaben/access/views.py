from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Permission, AccessCode
from access import serializers


class AccessCodeViewSet(viewsets.ModelViewSet):
    """ Events in database """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    queryset = AccessCode.objects.all()
    serializer_class = serializers.AccessCodeSerializer


class PermissionsViewSet(viewsets.ModelViewSet):
    """ Events in database """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    queryset = Permission.objects.all()
    serializer_class = serializers.PermissionsSerializer
