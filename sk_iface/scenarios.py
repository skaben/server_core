import logging
import time

from sk_iface.state_manager import GlobalStateManager
from sk_iface.models import MenuItem, Lock
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

channel_layer = get_channel_layer()


class CallbackManager():
    def __init__(self, **kw):
        self.kwargs = kw
    
    def _reload(self):
        msg = {
            'type': 'post.save',
            'name': 'full'
        }
        async_to_sync(channel_layer.send)('events', msg)
 
    def _switch_doors(self, val):
        res = []
        with GlobalStateManager() as manager:
            manager.locks.update(opened=val)
            for device in manager.locks:
                send_msg = {
                    'type': 'server.event',
                    'dev_type': 'lock',
                    'uid': device.uid
                }
                res.append(send_msg)
            for message in res:
                async_to_sync(channel_layer.send)('events', message)
        self._reload()

    def open_doors(self):
        logging.info('opening all doors')
        self._switch_doors(True)
        return 'doors forced open'

    def close_doors(self):
        logging.info('closing all doors')
        self._switch_doors(False)
        return 'doors forced closed'

    def serv_off(self):
        logging.info('servs offline')
        self._reload()
        return '! SERVITORS OFFLINE !' * 50

cb_manager = CallbackManager()
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
            gas_str = '/RGB/SLD/00FF00/S /STR/SLD/1/S /LGT/SLD/1/S'
            msg = {
                'type': 'mqtt.send',
                'dev_type': 'dumb',
                'uid': 'gas',
                'command': 'CUP',
                'task_id': '123123',
                'payload': {'config': gas_str}
            }
            async_to_sync(channel_layer.send)('mqtts', msg)
            return '! GAS REROUTED !' * 50
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
        if pl.get('comment') == 'serv_rep':
            return '! REPAIR SERVITORS ACTIVATED !' * 50
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
        if not hasattr(cb_manager, callback):
            _err = f'Callback Manager has no method for <{name}>'
            logging.error(_err)
            return _err
        else:
            return getattr(cb_manager, callback)()
            
         
            



