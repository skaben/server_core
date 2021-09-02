from core.views import DynamicAuthMixin
from eventlog import serializers
from rest_framework import viewsets, filters

from .models import EnergyState


class EnergyStateViewSet(viewsets.ModelViewSet, DynamicAuthMixin):
    """ Energy state cycles in database """
    queryset = EnergyState.objects.all()
    serializer_class = serializers.EnergyStateSerializer