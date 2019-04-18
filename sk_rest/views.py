from rest_framework import serializers, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response

from .models import Lock, Terminal
from .serializers import LockSerializer, TerminalSerializer

from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import UpdateModelMixin
from rest_framework.viewsets import ModelViewSet


class LockPartialUpdate(GenericAPIView, UpdateModelMixin):
    '''
    You just need to provide the field which is to be modified.
    '''
    queryset = Lock.objects.all()
    serializer_class = LockSerializer

    def post(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class ExampleView(APIView):
    """
    A view that can accept POST requests with JSON content.
    """

    def post(self, request, format=None):
        return Response({'received data': request.data})

    def get(self, request, format=None):
        terminals = Terminal.objects.all()
        serializer = TerminalSerializer(terminals, many=True)
        return Response(serializer.data)

# ViewSets define the view behavior.

class LockViewSet(viewsets.ModelViewSet):
    serializer_class = LockSerializer
    queryset = Lock.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('descr', 'opened')


class TerminalViewSet(viewsets.ModelViewSet):
    serializer_class = TerminalSerializer
    queryset = Terminal.objects.all()

