from rest_framework import serializers

from .models import EnergyState


class EnergyStateSerializer(serializers.ModelSerializer):
    """ Serializer for energy state objects """

    class Meta:
        model = EnergyState
        fields = '__all__'
