from django.core.exceptions import ObjectDoesNotExist

from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import AlertState
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

    def _update_counter(self, state):
        data = {'value': state.threshold,
                'comment': f'state changed to {state.name}'}
        serializer = serializers.AlertCounterSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
        else:
            # fixme: error handling?
            return serializer.errors

    def _update_others(self, state):
        try:
            other_states = self.queryset.exclude(id=state.id)
            other_states.update(current=False)
        except ObjectDoesNotExist:
            # TODO: here comes handling ... soon.
            pass

    # FIXME: move all logic to model method
    @action(detail=True, methods=['post'])
    def set_current(self, request, pk=None):
        """ Set alert state as current, reset other states to non-current"""
        new_state = self.get_object()
        serializer = serializers.AlertStateSerializer(data=request.data)
        if serializer.is_valid():
            # fix for multiple current flags set manually
            self._update_others(new_state)
            # state is already active, nothing to change
            if new_state.current:
                return Response({'status': f'state {new_state.name} '
                                           'is already active'})
            else:
                self._update_counter(new_state)
                new_state.current = True
                new_state.save()
                return Response({'status': f'changed to {new_state.name}'})
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

    queryset = AlertState.objects.all()
    serializer_class = serializers.AlertStateSerializer

    _ingame_states = AlertState.objects.filter(threshold__gt=0).all()
