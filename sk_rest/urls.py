from django.conf.urls import url
from django.urls import path, include
#from .urlrest import router  # separated REST urls
#from sk_rest import views

from .models import Lock, Dumb, Terminal
from rest_framework import routers, serializers, viewsets, generics
from django_filters.rest_framework import DjangoFilterBackend


class LockSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Lock
        fields = '__all__'


class TerminalSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Terminal
        fields = '__all__'


# ViewSets define the view behavior.

class LockViewSet(viewsets.ModelViewSet):
    serializer_class = LockSerializer
    queryset = Lock.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name', 'opened')


class TerminalViewSet(viewsets.ModelViewSet):
    queryset = Terminal.objects.all()
    serializer_class = TerminalSerializer


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()

# actual urls
router.register(r'dev/lock', LockViewSet)
router.register(r'dev/term', TerminalViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]