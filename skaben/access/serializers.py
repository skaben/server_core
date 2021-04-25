from rest_framework import serializers

from .models import AccessCode, Permission


class AccessCodeSerializer(serializers.ModelSerializer):
    """ Serializer for access code objects """

    class Meta:
        model = AccessCode
        fields = '__all__'
        read_only_fields = ('id',)


class PermissionSerializer(serializers.ModelSerializer):
    """ Serializer for lock-card relation objects """

    card = serializers.HyperlinkedIdentityField(view_name="api:accesscode-detail")
    lock = serializers.HyperlinkedIdentityField(view_name="api:lock-detail")
    state_id = serializers.HyperlinkedIdentityField(view_name="api:alertstate-detail", many=True)

    class Meta:
        model = Permission
        fields = "__all__"
