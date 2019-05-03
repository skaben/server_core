import logging
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, render_to_response
from django.core import serializers
from django.db import transaction
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger('skaben.sk_iface')

from .forms import LockForm, TerminalForm, StateForm, ValueForm
from .models import *

channel_layer = get_channel_layer()

# Create your views here.

def _get_context(k=None):
    context = dict()
    context['locks'] = Lock.objects.order_by('id')
    context['dumbs'] = Dumb.objects.order_by('id')
    context['terms'] = Terminal.objects.order_by('id')
    context['state'] = State.objects.order_by('id')
    context['value'] = -1
    context['log'] = Log.objects.all().order_by('-id')[:20][::-1]

    _permlist = Permission.objects.all()

    for lock in context['locks']:
        cards = _permlist.filter(lock_id=lock.id)
        for card in cards:
            state_list = list(card.state_id.values_list('id', flat=True))
            setattr(card, 'state_list', state_list)
        setattr(lock, 'cards', cards)
    try:
        context['value'] = Value.objects.order_by('id').reverse()[0]
    except IndexError:
        logging.exception('database contains no state value')
    return context


def index(request):
    # split to views
    context = _get_context()
    return render(request, 'index.html', {'context': context,
                                          'stateform': StateForm(),
                                          'lockform': LockForm(),
                                          'termform': TerminalForm()})

def log(request):
    context = Log.objects.all().order_by('-id')
    return render(request, 'log.html', {'log_records': context})


def terminal(request, pk):
    terminal = Terminal.objects.get(pk=pk)
    if request.method == 'POST':
        form = TerminalForm(request.POST, instance=terminal)
        if form.is_valid():
            form.save()
            return JsonResponse({'result': 'good'})
        else:
            return JsonResponse({'result': 'bad'})


def lock(request, pk):
    lock = Lock.objects.get(pk=pk)
    try:
        if request.method == 'POST':
            postdata = request.POST.copy()
            status = postdata.get('status')
            try:
                states = State.objects.all()
                permissions = Permission.objects.all()
                card_values = {k.split('-')[-1]:postdata.getlist(k) for k in
                               postdata if k.startswith('state')}
                with transaction.atomic():
                    logger.info(card_values)
                    for card in card_values:
                        active_states_pk = card_values[card]
                        for perm in permissions.filter(pk=int(card)):
                            perm.state_id.set(active_states_pk, clear=True)
                            perm.save()
            except:
                logger.exception('bad permission list')

            if status == 'closed':
                postdata.update({'opened': 0, 'blocked': 0})
            elif status == 'opened':
                postdata.update({'opened': 1, 'blocked': 0})
            elif status == 'blocked':
                postdata.update({'blocked': 1})
            form = LockForm(postdata, instance=lock)
            if form.is_valid():
                form.save()
                serialized_lock = serializers.serialize('json', [lock, ])
                return JsonResponse({'result': 'updated successfully',
                                     'data': serialized_lock})
            else:
                return JsonResponse({'result': 'device cannot be updated'})
    except:
        raise

def change_state(request):
    value_form = None
    current_name = 'missing'
    states = State.objects.all()
    current_state = states.filter(current=True).first()
    if current_state:
        current_name = current_state.name
    last_value = Value.objects.all().latest('id')
    if request.method == 'POST':
        value = int(request.POST.get('value', last_value.value))
        state_name = request.POST.get('name', current_name)
        if value == last_value.value and state_name == current_name:
            return JsonResponse({'result': 'nothing to update'})

        if value != last_value.value:
            value_form = ValueForm({'value': int(value),
                                    'comment': 'from web interface'})
        try:
            # avoiding duplicate post_save signal generation
            with transaction.atomic():
                if value_form:
                    value_form.save()
                if state_name != current_name:
                    for s in states:
                        # multi-'current' status should be avoided by any cost
                        # double save to avoid saving all objects in queryset
                        if s.current:
                            s.current = False
                            s.save()
                        elif s.name == state_name:
                            current_state = s
            # well, Django doesn't generate signals after transaction.
            # so, saving our precious outside the transaction
            current_state.update(current=True)  # yay, post_save signal
            # generated!
        except:
            raise

    return JsonResponse({'result': 'success'})

def sendlog(request, msg=None):
    if msg == None:
        msg = {'message': 'test'}
    cmd = {
        'type': 'ws.log',
    }
    cmd.update(msg)
    async_to_sync(channel_layer.send)('events', cmd)
    return HttpResponse(f'send test msg', content_type='text/plain')

