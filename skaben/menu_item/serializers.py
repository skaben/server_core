from rest_framework import serializers

from core.models import MenuItem, WorkMode


class MenuItemSerializer(serializers.ModelSerializer):
    """ Serializer for menu item objects """

    class Meta:
        model = MenuItem
        fields = '__all__'
        read_only_fields = ('id',)


class WorkModeSerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkMode
        fields = '__all__'
        read_only_fields = ('id',)