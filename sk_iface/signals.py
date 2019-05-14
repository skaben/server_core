from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Dumb, Terminal, Lock, State

channel_layer = get_channel_layer()

def device_handler(device, update_fields, instance):
    msg = {
        'type': 'post.save',
        'name': device,
        'id': instance.id,
    }

    # TODO
    # currently - there's too many fields updating via Forms.
    # number of fields should be shortened and true partial update achieved
    if update_fields:
        if len(update_fields) == 1 and 'ts' in update_fields:
            return  # no action, it's ping
        # converting frozenset
        update_fields_set = tuple(uf for uf in update_fields)
        msg.update({'updated': update_fields_set})

    async_to_sync(channel_layer.send)('events', msg)


@receiver(post_save, sender=Lock)
def lock_handler(sender, update_fields, created, instance, **kwargs):
    device_handler('lock', update_fields, instance)

@receiver(post_save, sender=Terminal)
def term_handler(sender, update_fields, created, instance, **kwargs):
    device_handler('term', update_fields, instance)

@receiver(post_save, sender=Dumb)
def dumb_handler(sender, update_fields, created, instance, **kwargs):
    device_handler('dumb', update_fields)

@receiver(post_save, sender=State)
def alert_handler(sender, **kwargs):
    msg = {
        'type': 'post.save',
        'name': 'full'
    }
    async_to_sync(channel_layer.send)('events', msg)