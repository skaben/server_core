from rest_framework import serializers

from core.models import Lock, Terminal, Tamed, Permission


class LockSerializer(serializers.ModelSerializer):
    """ Serializer for lock objects """

    acl = serializers.ReadOnlyField()
    permissions = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='permission-detail',
        read_only=True
    )

    class Meta:
        model = Lock
        fields = '__all__'
        read_only_fields = ('id',)


class TerminalSerializer(serializers.ModelSerializer):
    """ Serializer for terminal objects """

    class Meta:
        model = Terminal
        fields = '__all__'
        read_only_fields = ('id',)


class TamedSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tamed
        fields = '__all__'
        read_only_fields = ('id',)
