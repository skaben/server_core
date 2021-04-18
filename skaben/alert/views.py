from alert import serializers
from core.models import AlertCounter, AlertState
from core.views import DynamicAuthMixin
from django.core.exceptions import ObjectDoesNotExist
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class AlertStateViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet,
                        DynamicAuthMixin):
    """ Global alert state viewset

        warn: only partial_update is allowed - see readonly field in serializer
    """
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
        update_data = {'current': True}
        serializer = serializers.AlertStateSerializer(instance=state,
                                                      data=update_data)
        if serializer.is_valid():
            serializer.update(state, update_data)
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
    queryset = AlertCounter.objects.all()
    serializer_class = serializers.AlertCounterSerializer
