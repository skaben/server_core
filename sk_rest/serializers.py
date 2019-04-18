from .models import Lock, Dumb, Terminal
from rest_framework import serializers

class LockSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Lock
        fields = '__all__'


class TerminalSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Terminal
        fields = ('descr',
                  'powered',
                  'override',
                  'hacked',
                  'blocked',
                  'hack_attempts',
                  'hack_length',
                  'hack_wordcount',
                  'menu_list',
                  'msg_header',
                  'msg_body')

