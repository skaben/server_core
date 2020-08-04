from django.core.exceptions import ObjectDoesNotExist

from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from django_filters.rest_framework import DjangoFilterBackend

from core.models import AlertState, AlertCounter
from alert import serializers


class AlertStateViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    """ Global alert state viewset

        warn: only partial_update is allowed - see readonly field in serializer
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    queryset = AlertState.objects.all()
    serializer_class = serializers.AlertStateSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['current']

    @action(detail=True, methods=['get'])
    def set_current(self, request, pk=None):
        """ Set current """
        try:
            state = self.queryset.get(id=pk)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        # calling update, passing instance
        serializer = serializers.AlertStateSerializer(instance=state,
                                                      data={'current': True})
        if serializer.is_valid():
            serializer.save()
            return Response('state successfully updated',
                            status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class AlertCounterViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          mixins.CreateModelMixin,
                          viewsets.GenericViewSet):
    """
        Alert counter viewset
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    queryset = AlertCounter.objects.all()
    serializer_class = serializers.AlertCounterSerializer
