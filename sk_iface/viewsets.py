from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from sk_iface.models import *
from sk_iface.serializers import *

class StateViewSet(viewsets.ModelViewSet):
    queryset = State.objects.all()
    serializer_class = StateSerializer
    # no modifications through rest api
    http_method_names = ['get', 'head', 'post']

    # no creation, only change 'current' flag
    # yes, this is twisted and I don't know how to use serializers properly
    def create(self, request):
        ssr = StateSerializer()
        result = ssr.update(request.data)
        return Response(result, status=status.HTTP_201_CREATED)


class ValueViewSet(viewsets.ModelViewSet):
    queryset = Value.objects.all()
    serializer_class = ValueSerializer


class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer

    def get_queryset(self):
        queryset = self.queryset
        lock_id = self.request.query_params.get('lock_id', None)
        if lock_id:
            queryset = queryset.filter(lock_id=lock_id)
        return queryset

class LockViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Lock.objects.all().order_by('descr')
    serializer_class = LockSerializer


class TerminalViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Terminal.objects.all().order_by('descr')
    serializer_class = TerminalSerializer


class CardViewSet(viewsets.ModelViewSet):
    queryset = Card.objects.all().order_by('surname')
    serializer_class = CardSerializer


class InfoTextViewSet(viewsets.ModelViewSet):
    queryset = Text.objects.all()
    serializer_class = InfoTextSerializer


class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
