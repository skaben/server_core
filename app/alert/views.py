from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import AlertState
from alert import serializers


class AlertStateViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        viewsets.GenericViewSet):
    """ Manage global alert states

        warn: only partial_update is allowed - see readonly field in serializer
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    queryset = AlertState.objects.all()
    serializer_class = serializers.AlertStateSerializer
