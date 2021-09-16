from core.views import DynamicAuthMixin
from actions import serializers
from rest_framework import viewsets, filters

from .models import EnergyState


class EnergyStateViewSet(viewsets.ModelViewSet, DynamicAuthMixin):
    """ Energy state cycles in database """
    queryset = EnergyState.objects.all().order_by('-id')[:1]
    serializer_class = serializers.EnergyStateSerializer

