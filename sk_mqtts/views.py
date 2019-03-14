from django.http import HttpResponse
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

channel_layer = get_channel_layer()

def mqtt_start(request):
    cmd = {
            'type': 'app_control',
            'mqtt': 'start'
        }
    async_to_sync(channel_layer.send)('app_control', cmd)
    return HttpResponse(f'starting mqtt server', content_type='text/plain')


def mqtt_stop(request):
    cmd = {
            'type': 'app_control',
            'mqtt': 'stop'
        }
    async_to_sync(channel_layer.send)('app_control', cmd)
    return HttpResponse(f'stopping mqtt server', content_type='text/plain')


def mqtt_send(request):
    test_msg = {
                'type': 'mqtt_send',
                'command': 'ACK',
                'dev_type': 'lock',
                'dev_name': 'lock0',
                'task_id': '12314514'
               }
    async_to_sync(channel_layer.send)('mqtt_send', test_msg)
    return HttpResponse(f'send msg {test_msg}', content_type='text/plain')