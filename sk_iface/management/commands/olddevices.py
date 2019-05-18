from django.core.management.base import BaseCommand, CommandError
from sk_iface.misc import get_online_devices

class Command(BaseCommand):
    help = 'check all devices for old timestamp'

    def handle(self, *args, **kwargs):
        devices = get_online_devices()
        for device_type in devices.values():
            for device in device_type:
                # check is it really online by comparing device ts with current time
                if device.offline:
                    # hippity-hoppity, offline is property
                    device.online = False
                    # not atomic for proper post_save signal generation
                    device.save(update_fields=['online'])



