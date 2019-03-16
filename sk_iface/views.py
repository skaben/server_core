from django.http import HttpResponse
from django.shortcuts import render, render_to_response
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from sk_rest import models

channel_layer = get_channel_layer()

# Create your views here.

def index(request):
    locks = models.Lock.objects.order_by('id')
    terms = models.Terminal.objects.order_by('id')
    dumbs = models.Dumb.objects.order_by('id')

    context = {'locks': locks,
               'terms': terms,
               'dumbs': dumbs}

    return render(request, 'index.html', context)


def sendlog(request, msg=None):
    if msg == None:
        msg = {'message': 'test'}
    cmd = {
        'type': 'sendlog',
    }
    cmd.update(msg)
    print(f'sending {msg}')
    async_to_sync(channel_layer.send)('events', msg)
    return HttpResponse(f'send test msg', content_type='text/plain')
