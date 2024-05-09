from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer
from peripheral_behavior.models import MenuItem, MenuItemAudio, MenuItemImage, MenuItemVideo


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ("timer", "description")


class MenuItemAudioSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItemAudio
        fields = MenuItemSerializer.Meta.fields + ("content",)


class MenuItemVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItemVideo
        fields = MenuItemSerializer.Meta.fields + ("content",)


class MenuItemImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItemImage
        fields = MenuItemSerializer.Meta.fields + ("test_value",)


class MenuPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        MenuItemVideo: MenuItemVideoSerializer,
        MenuItemAudio: MenuItemAudioSerializer,
        MenuItemImage: MenuItemImageSerializer,
    }
