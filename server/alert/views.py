from alert import serializers
from core.views import DynamicAuthMixin
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import AlertCounter, AlertState


class AlertStateViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet, DynamicAuthMixin):
    """Global alert state viewset"""

    queryset = AlertState.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["current"]

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.AlertStateSerializer
        if self.action == 'set_current':
            return serializers.AlertStateSetCurrentSerializer
        else:
            return serializers.AlertStateSerializer

    @action(detail=True, methods=["post"])
    def set_current(self, request, pk=None):
        """Set Alert State as current"""
        try:
            state = self.queryset.get(id=pk)
            serializer = self.get_serializer_class()(AlertState, data=request.data)
            if serializer.is_valid():
                if not serializer.data.get('current'):
                    return Response(f"state current cannot be unset - only switched to another state")
                if state.current:
                    return Response(f"state already set to current")
                state.current = True
                state.save()
                serializer_resp = serializers.AlertStateSerializer(state)
                return Response(serializer_resp.data)
            else:
                return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except AlertState.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except:
            return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class AlertCounterViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet
):
    """
    Alert counter viewset
    """

    queryset = AlertCounter.objects.all()
    serializer_class = serializers.AlertCounterSerializer

    @action(detail=False)
    def get_latest(self, *args, **kwargs):
        try:
            latest = AlertCounter.objects.latest("id")
        except AlertCounter.DoesNotExist:
            latest = AlertCounter.objects.create_initial()

        serializer = self.get_serializer(latest)
        return Response(serializer.data)
