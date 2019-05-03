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
    # TODO: error handling
    print(msg)
    #if not update_fields:
    #    return
    #if len(update_fields) == 1:
    #    if 'ts' in update_fields:
    #        return
    async_to_sync(channel_layer.send)('events', msg)


@receiver(post_save, sender=Lock)
def lock_handler(sender, update_fields, created, instance, **kwargs):
    device_handler('lock', update_fields, instance)

@receiver(post_save, sender=Terminal)
def term_handler(sender, update_fields, created, instance, **kwargs):
    device_handler('term', update_fields)

@receiver(post_save, sender=Dumb)
def term_handler(sender, update_fields, created, instance, **kwargs):
    device_handler('dumb', update_fields)

@receiver(post_save, sender=State)
def alert_handler(sender, **kwargs):
    msg = {
        'type': 'post.save',
        'name': 'full'
    }
    async_to_sync(channel_layer.send)('events', msg)