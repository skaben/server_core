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
from .misc import GlobalStateManager

channel_layer = get_channel_layer()

# Create your views here.

def _get_context(k=None):
    context = dict()

    # TODO: there should be normal forms!!

    context['locks'] = Lock.objects.order_by('id')
    context['dumbs'] = Dumb.objects.order_by('id')
    context['terms'] = Terminal.objects.order_by('id')
    context['state'] = State.objects.order_by('id')
    context['value'] = -1
    context['log'] = Log.objects.all().order_by('-id')[:20][::-1]

    _permlist = Permission.objects.all()
    _txtlist = Text.objects.all()

    context['texts'] = _txtlist

    for term in context['terms']:
        texts = _txtlist.filter(device=term.id)
        setattr(term, 'texts', texts)

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

# TODO: form error manage

def terminal(request, pk):
    terminal = Terminal.objects.get(pk=pk)
    if request.method == 'POST':
        postdata = request.POST.copy()
        text_id = postdata.get('infotext')
        status = postdata.get('status')
        if text_id: # not default
            text = Text.objects.get(pk=text_id)
            text.device.set(postdata.get('id'), clear=True)
            # TODO: should be managed by DB
            postdata.update({'msg_body': text.content,
                             'msg_header': text.title})
        else:
            postdata.update({'msg_body': '-',
                             'msg_header': '-'})
        if status == 'normal':
            postdata.update({'blocked': 0, 'hacked': 0})
        elif status == 'hacked':
            postdata.update({'hacked': 1, 'blocked': 0})
        elif status == 'blocked':
            postdata.update({'hacked': 0, 'blocked': 1})
        postdata.update({'menu_list': 'default'})
        # todo: get rid of it with normal form management
        if not postdata.get('powered'):
            postdata.update({'powered': False})
        form = TerminalForm(postdata, instance=terminal)
        try:
            if form.is_valid():
                form.save(commit=False)
                update_fields=[k for k in postdata if k in
                               terminal.__dict__.keys()]
                terminal.save(update_fields=update_fields)
                serialized_term = serializers.serialize('json', [terminal, ])
                # send config to device
                send_msg =  {'type': 'server.event',
                             'uid': terminal.uid,
                             'dev_type': 'term',
                            }
                async_to_sync(channel_layer.send)('events', send_msg)
                return JsonResponse({'result': 'updated successfully',
                                     'data': serialized_term})
            else:
                logger.error(form.errors)
                return JsonResponse({'error': 'form.errors'})
        except:
            logger.exception('cannot save terminal')
            return JsonResponse({'data': 'bad'})


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
            if not postdata.get('sound'):
                postdata.update({'sound': False})
            form = LockForm(postdata, instance=lock)
            if form.is_valid():
                form.save(commit=False)
                update_fields=[k for k in postdata if k in lock.__dict__.keys()]
                lock.save(update_fields=update_fields)
                send_msg = {'type': 'server.event',
                            'uid': lock.uid,
                            'dev_type': 'lock',
                           }
                async_to_sync(channel_layer.send)('events', send_msg)
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
            if value_form:
                value_form.save()

        try:
            with GlobalStateManager() as manager:
                manager.set_state(state_name, manual=True)
                devices = manager.device_update_list()


                # TODO: MANAGE TRUE BROADCAST for same packets

                for dt in devices.items():
                    device_type = dt[0]
                    bcast_devices = dt[1]

                    # sending update message to every device in receivers list
                    for device in bcast_devices:
                        send_msg = {
                            'type': 'server.event',
                            'dev_type': device_type,
                            'uid': device.uid
                        }
                        async_to_sync(channel_layer.send)('events', send_msg)
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

