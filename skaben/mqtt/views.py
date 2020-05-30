import time
import json
import multiprocessing as mp

from rest_framework.decorators import api_view

from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

import skabenproto

from core.models import MQTTMessage
from mqtt import serializers
from core.rabbit.main import run_workers, run_pinger, stop_all


@api_view(http_method_names=['GET'])
def start(request):
    try:
        workers = run_workers()
        return Response(workers)
    except Exception as e:
        return Response({'exception': f'{e}'},
                        status=status.HTTP_403_FORBIDDEN)


@api_view(http_method_names=['GET'])
def stop(request):
    try:
        results = stop_all()
        return Response(results)
    except Exception as e:
        return Response({'exception': f'{e}'},
                        status=status.HTTP_403_FORBIDDEN)


@api_view(http_method_names=['GET'])
def ping(request):
    try:
        pinger = run_pinger()
        return Response(pinger)
    except Exception as e:
        return Response({'exception': f'{e}'},
                        status=status.HTTP_403_FORBIDDEN)


class MQTTMessageViewSet(viewsets.ModelViewSet):
    """ MQTT message all """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    queryset = MQTTMessage.objects.all()
    serializer_class = serializers.MQTTMessageSerializer

