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
from mqtt import serializers, server
from core.rabbit.main import run_workers


@api_view(http_method_names=['GET'])
def start(request):
    try:
        workers = run_workers()
        return Response(workers)
    except Exception as e:
        return Response({'exception': f'{e}'},
                        status=status.HTTP_403_FORBIDDEN)

#    try:
#        result = server.interface.start()
#        return Response({'status': result}, status=200)
#    except Exception as e:
#        content = {'status': 'server start failed', 'exception': f'{e}'}
#        return Response(content, status=200)


@api_view(http_method_names=['GET'])
def stop(request):
    #return Response(f'{drain()}')
    return Response('{drain()}')

#    try:
#        result = server.interface.stop()
#        return Response({'status': result}, status=status.HTTP_200_OK)
#    except Exception as e:
#        content = {'status': 'server stop failed', 'exception': f'{e}'}
#        return Response(content, status=status.HTTP_204_NO_CONTENT)


#@api_view(http_method_names=['GET'])
def current(request):
    return 'current'
#    kombu_cons()
#    return Response(f'{len(listttt)}' + '<hr>' +
#                    ''.join([f'<p>{x}</p>' for x in listttt]))
#    try:
#        mqtts = server.interface.server_instance
#        if not mqtts:
#            content = {'status': 'server instance not created, start server first'}
#        else:
#            content = {
#                'connected': mqtts.is_connected,
#                'running': mqtts.running,
#                'qos': mqtts.qos,
#                'publish': mqtts.publish_to,
#                'listen': [name for (name, qos) in mqtts.listen_to],
#            }
#        return Response(content, status=status.HTTP_200_OK)
#    except Exception as e:
#        return Response({'exception': f'{e}'}, status=status.HTTP_204_NO_CONTENT)


def send_message(request):
    return Response('')
#    serializer = serializers.MQTTMessageSerializer(data=request.data)
#    if serializer.is_valid():
#        serializer.save()
#        with skabenproto.PacketEncoder() as context:
#            cmd = request.data.pop('command')
#            packet = context.load(cmd, **request.data)  # load data to packet
#            encoded = context.encode(packet, timestamp=int(time.time()))  # encode to MQTT format
#            server.server_instance.publish(encoded)  # let the package fly
#        return Response({'status': 'message sent', 'data': json.dumps(request.data)})
#    else:
#        return Response(serializer.errors,
#                        status=status.HTTP_400_BAD_REQUEST)


class MQTTMessageViewSet(viewsets.ModelViewSet):
    """ MQTT message all """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    queryset = MQTTMessage.objects.all()
    serializer_class = serializers.MQTTMessageSerializer


#
#class MQTTMessageDeliveredViewSet(MQTTMessageViewSet):
#    """ MQTT message delivered successfully """
#
#    queryset = MQTTMessage.objects.filter(delivered=True).all()
#
#
#class MQTTMessageNotDeliveredViewSet(MQTTMessageViewSet):
#    """ MQTT message delivery failed """
#
#    queryset = MQTTMessage.objects.filter(delivered=False).all()


