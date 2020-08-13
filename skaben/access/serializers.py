from rest_framework import serializers

from core.models import Permission, AccessCode


class PermissionsSerializer(serializers.HyperlinkedModelSerializer):
    """ Serializer for lock-card relation objects """

    acl_full = serializers.ReadOnlyField()
    url = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='permission-detail'
    )

    class Meta:
        model = Permission
        fields = '__all__'
        read_only_fields = ('id',)


class AccessCodeSerializer(serializers.HyperlinkedModelSerializer):
    """ Serializer for access code objects """

    url = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='accesscode-detail'
    )

    class Meta:
        model = AccessCode
        fields = '__all__'
        read_only_fields = ('id',)


# class PermissionsSerializer(serializers.ModelSerializer):
#     """ Serializer for lock-card relation objects """

    # acl_full = serializers.ReadOnlyField()

    # class Meta:
    #     model = Lock
    #     fields = ('id', 'acl_full')
    #     read_only_fields = ('id',)
