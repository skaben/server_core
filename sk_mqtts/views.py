# bad code placing. REFACTORING

from django.http import HttpResponse
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

channel_layer = get_channel_layer()

def mqtt_start(request):
    cmd = {
            'type': 'mqtt.start',
        }
    async_to_sync(channel_layer.send)('mqtts', cmd)
    return HttpResponse(f'starting mqtt server', content_type='text/plain')


def mqtt_stop(request):
    cmd = {
            'type': 'mqtt.stop',
        }
    async_to_sync(channel_layer.send)('mqtts', cmd)
    return HttpResponse(f'stopping mqtt server', content_type='text/plain')


def mqtt_send(request):
    test_msg = {
                'type': 'mqtt.send',
                'command': 'ACK',
                'dev_type': 'lock',
                'uid': 'lock0',
                'task_id': '12314514'
               }
    async_to_sync(channel_layer.send)('mqtts', test_msg)
    return HttpResponse(f'send msg {test_msg}', content_type='text/plain')


def mqtt_to_event(request, packet=None):
    """
        passes mqtt data to Redis-backed channel layer, where it should be parsed!

    :param request:
    :param packet: data from device or test payload from endpoint
    :return: httpresponce (endpoint only)
    """
    if not packet:
        packet = {'test': 'test'}

    msg = {
        'type': 'device.event',
    }
    msg.update(packet)
    async_to_sync(channel_layer.send)('events', msg)

    if not packet:
        return HttpResponse(f'send test msg {msg}', content_type='text/plain')
    else:
        return True
