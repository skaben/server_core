from django.shortcuts import render, render_to_response
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

channel_layer = get_channel_layer()

# Create your views here.

def index(request):
    return render_to_response('index.html')


