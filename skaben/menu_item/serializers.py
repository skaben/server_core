from rest_framework import serializers

from core.models import MenuItem


class MenuItemSerializer(serializers.ModelSerializer):
    """ Serializer for menu item objects """

    class Meta:
        model = MenuItem
        fields = '__all__'
        read_only_fields = ('id',)
