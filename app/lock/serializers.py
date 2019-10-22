from rest_framework import serializers

from core.models import Lock


class LockSerializer(serializers.HyperlinkedModelSerializer):
    """ Serializer for lock objects """

    class Meta:
        model = Lock
        fields = '__all__'
        read_only_fields = ('id', 'acl_all')
        view_name = 'lock-details'
