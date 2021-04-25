from rest_framework import serializers

from .models import Action, UserInput


class UserInputSerializer(serializers.ModelSerializer):
    """ Serializer for menu item objects """

    class Meta:
        model = UserInput
        exclude = ("id", "name",)


class ActionSerializer(serializers.ModelSerializer):
    """ Serializer for action objects """

    class Meta:
        model = Action
        exclude = ("id", "name",)
