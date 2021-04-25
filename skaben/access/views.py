from access import serializers
from core.views import DynamicAuthMixin
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .models import AccessCode, Permission


class AccessCodeViewSet(viewsets.ModelViewSet, DynamicAuthMixin):
    """ Events in database """
    queryset = AccessCode.objects.all()
    serializer_class = serializers.AccessCodeSerializer


class PermissionViewSet(viewsets.ModelViewSet, DynamicAuthMixin):
    """ Events in database """
    queryset = Permission.objects.all()
    serializer_class = serializers.PermissionSerializer
