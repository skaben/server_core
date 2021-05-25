from alert import serializers
from core.views import DynamicAuthMixin
from django.core.exceptions import ObjectDoesNotExist
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.views.decorators.http import require_http_methods

from .models import AlertCounter, AlertState


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

    def _set_current(self, state):
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

    @action(detail=False, methods=['post'])
    def set_current_by_name(self, request):
        try:
            name = request.data.get('name')
            if not name:
                raise ObjectDoesNotExist
            state = AlertState.objects.filter(name=name).first()
            return self._set_current(state)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def set_current(self, request, pk=None):
        """ Set Alert State as current """
        try:
            state = self.queryset.get(id=pk)
            return self._set_current(state)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class AlertCounterViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          mixins.CreateModelMixin,
                          viewsets.GenericViewSet):
    """
        Alert counter viewset
    """
    queryset = AlertCounter.objects.all()
    serializer_class = serializers.AlertCounterSerializer

    @action(detail=False)
    def get_latest(self, *args, **kwargs):
        latest = AlertCounter.objects.latest('id')
        serializer = self.get_serializer(latest)
        return Response(serializer.data)
