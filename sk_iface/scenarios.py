import logging
import time

from sk_iface.state_manager import GlobalStateManager
from sk_iface.models import MenuItem
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

channel_layer = get_channel_layer()


class CallbackManager():
    def __init__(self, device=None):
        self.dev = device

    def magos_pass(self):
        logging.info('passcode received')

    def easier(self):
        logging.info('set minigame easier')

    def all_doors(self):
        logging.info('switch all doors')
        # open all doors
        pass

    def serv_off(self):
        logging.info('servs offline')
        pass


manager = CallbackManager()
callbacks = MenuItem.objects.filter(callback__isnull=False).values('callback')

# session variables

magos_password = 'thevoid'
tech_password = 'thesoul'


def parse_scenario(msg, dev, orm):
    pl = dev.payload

    if not msg:
        return
    else:
        msg = msg.strip()

    # alert level changes
    if msg == 'alert':
        alert_value = pl.get('level', None)
        if alert_value == 'reset':
            with GlobalStateManager() as manager:
                # only if in playable mode
                if manager.current in manager.playable:
                    manager.set_state('green', manual=True)
                    return 'ALERT LOWERED'
                else:
                    return 'TRYING TO LOWER ALERT IN NON-PLAYABLE MODE'
        message = pl.get('comment', 'value changed')
        if not alert_value:
            msg = 'no alert level to change'
            logging.error(msg)
            return msg
        with GlobalStateManager() as manager:
            manager.change_value(alert_value,
                                 message)
        return f'{dev.dev_type}/{dev.uid} {message}'
    # check passwords
    if msg == magos_password: 
        if pl.get('comment') == 'gas':
            # send custom config to RGB
            return '! GAS REROUTED !' * 30
        else:
            orm.hacked = True
            orm.save(update_fields=('hacked',)) 
            send_msg = {'type': 'server.event',
                        'uid': orm.uid,
                        'dev_type': 'term'}
            time.sleep(10)
            async_to_sync(channel_layer.send)('events', send_msg)
            return 'magos password entered, terminal hacked'
    if msg == tech_password:
        orm.hack_difficulty = orm.easy
        orm.save(update_fields=('hack_difficulty',))
        # TODO: uniform message sending
        send_msg =  {'type': 'server.event',
             'uid': orm.uid,
             'dev_type': 'term',
            }
        time.sleep(10)
        async_to_sync(channel_layer.send)('events', send_msg)
        return 'tech password entered'
    # open\close lock events
    if msg.startswith('lock'):
        code = msg.split()[-1]
        return f'{dev.uid} {msg}'
    if msg == 'custom':
        callback = pl.get('callback', None) 
        # todo: exception management
#        if callback not in callbacks:
#            _err = f'callback name not exists: {callback}'
#            logging.error(_err)
#            return _err
        if not hasattr(manager, name):
            _err = f'Callback Manager has no method for <{name}>'
            logging.error(_err)
            return _err
        else:
            return getattr(manager, name)(device=dev)
            
         
            



