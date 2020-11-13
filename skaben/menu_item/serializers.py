from collections import OrderedDict
from rest_framework import serializers

from core.models import MenuItem, WorkMode


class MenuItemSerializer(serializers.ModelSerializer):
    """ Serializer for menu item objects """
    def to_representation(self, instance):
        result = super().to_representation(instance)
        return OrderedDict([(key, result[key]) for key in result if result[key] is not None])

    class Meta:
        model = MenuItem
        fields = '__all__'
        read_only_fields = ('id',)


class WorkModeSerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkMode
        fields = '__all__'
        read_only_fields = ('id',)