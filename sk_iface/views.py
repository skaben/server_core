from django.http import HttpResponse
from django.shortcuts import render, render_to_response
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.shortcuts import get_object_or_404, redirect
from sk_rest import serializers
from .forms import LockForm, TerminalForm
from sk_rest import models

from rest_framework.response import Response
from rest_framework.decorators import api_view

channel_layer = get_channel_layer()

# Create your views here.

def index(request):
    locks = models.Lock.objects.order_by('id')
    terms = models.Terminal.objects.order_by('id')
    dumbs = models.Dumb.objects.order_by('id')

    context = {'locks': locks,
               'terms': terms,
               'dumbs': dumbs}

    return render(request, 'index.html', {'context': context,
                                          'lockform': LockForm(),
                                          'termform': TerminalForm()})
                                          # TODO: migrate to DRF
                                          #'lockform': serializers.LockSerializer()})


def sendlog(request, msg=None):
    if msg == None:
        msg = {'message': 'test'}
    cmd = {
        'type': 'ws.log',
    }
    cmd.update(msg)
    async_to_sync(channel_layer.send)('events', cmd)
    return HttpResponse(f'send test msg', content_type='text/plain')
