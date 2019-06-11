import logging
import json
from django.db import transaction
from .models import Lock, Terminal, Dumb, State, Value, DevConfig, Permission
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger('skaben.sk_iface')
channel_layer = get_channel_layer()

class GlobalStateManager:

    playable = ['green', 'yellow', 'red']
    broadcast = dict()

    def __init__(self):
        self.locks = Lock.objects.all()
        self.terms = Terminal.objects.all()
        self.dumbs = Dumb.objects.all()
        self.states = State.objects.all()
#        self.test()
        self.current = self.states.filter(current=True).first()

    def test(self):
        for lock in self.locks:
            logger.info(lock.to_dict())
        #return self.get_lock_permissions(1)

    def set_state(self, name, manual=None):
        # normal procedure
        if hasattr(self, name):
            if name != 'white':
                # exclude all manual controlled device from updates
                self.locks = self.locks.exclude(override=True)
                self.terms = self.terms.exclude(override=True)
            if name in self.playable:
                if manual:
                    # set exactly this color
                    self._reset_threshold(name)
                    self.state(name)
                else:
                    # set state based on current alert value
                    V = Value.objects.all().latest('id')
                    return self.state_based_on_value(V.value)
            else:
                return self.state(name)

    def state_based_on_value(self, value):
        new_state = None
        for state in self.states:
            if value >= state.threshold:
                new_state = state
        if new_state:
            return self.state(new_state.name)

    def state(self, name):
        logger.info(f'setting state: {name}')
        if hasattr(self, name):
            if name == self.current.name:
                # already running in this state...
                return
            try:
                call = getattr(self, name)
                return call()
            except:
                raise

    def white(self):
        # ok, dungeon reset and all devices should be bulk updated
        self.locks.update(opened=True,
                          sound=False,
                          override=False,
                          blocked=False,
                          timer=10)
        self.terms.update(powered=False,
                          override=False,
                          blocked=False,
                          hacked=False,
                          hack_difficulty=6,
                          hack_wordcount=16,
                          hack_chance=10,
                          hack_attempts=4)
        for term in self.terms:
            term.msg_body.clear()
            term.menu_hacked.clear()
            term.menu_normal.clear()
        self.set_as_current('white')

    def blue(self):
        # only bool values are changed, avoiding rewrite white-phase-setup
        self.locks.update(opened=False,
                          sound=True,
                          blocked=False)
        self.terms.update(powered=False,
                          blocked=False,
                          hacked=False)
        self.set_as_current('blue')

    def cyan(self):
        self.locks.update(opened=False,
                          sound=True,
                          blocked=False)
        self.terms.update(powered=False,
                          blocked=False,
                          hacked=False)
        self.set_as_current('cyan')

    def green(self):
        self.locks.exclude(override=True).update(
            opened=False,
            sound=True,
        )
        self.terms.exclude(override=True).update(
            powered=True,
            blocked=False,
            hacked=False,
            hack_wordcount=16,
            hack_attempts=4,
            hack_difficulty=6
        )
        self.set_as_current('green')

    def yellow(self):
        self.locks.exclude(override=True).update(
            opened=False,
            sound=True,
        )
        self.terms.exclude(override=True).update(
            powered=True,
            blocked=False,
            hacked=False,
            hack_wordcount=16,
            hack_attempts=4,
            hack_difficulty=8
        )
        self.set_as_current('yellow')

    def red(self):
        self.locks.exclude(override=True).update(
            opened=False,
            sound=True,
        )
        self.terms.exclude(override=True).update(
            powered=True,
            blocked=False,
            hacked=False,
            hack_wordcount=16,
            hack_attempts=4,
            hack_difficulty=10,
        )
        self.set_as_current('red')

    def black(self):
        self.locks.update(
            opened=False,
            sound=True,
            blocked=True,
        )
        self.terms.update(
            powered=True,
            blocked=False,
            hacked=False,
            hack_wordcount=16,
            hack_attempts=4,
            hack_difficulty=12,
        )
        self.set_as_current('black')

    def set_as_current(self, name):
        try:
            other_states = self.states.exclude(name=name)
            other_states.update(current=False)
            new_state = self.states.filter(name=name).first()
            new_state.current = True
            new_state.save()
            self.send_unicast()
            self.send_broadcast(name)
        except:
            raise

    def _reset_threshold(self, name):
        threshold = self.states.filter(name=name).first().threshold
        if threshold < 0:
            return
        new_val = Value.objects.create(value=threshold,
                                       comment='level change auto-reset')
        new_val.save()

    def unicast_devices(self):
        locks = self.locks.filter(online=True).all()
        terms = self.terms.filter(online=True).all()
       
        return {
            'lock': locks,
            'term': terms,
        }

    def broadcast_devices(self, name):
        broadcast = {}
        dumb_conf = DevConfig.objects.filter(state_name=name).all()
        if dumb_conf:
            for d in dumb_conf:
                # todo: refactor later for every device type
                # update with types
                broadcast.update({d.dev_subtype: d.config})
            return broadcast
        else:
            logger.error('no devices set for broadcast')

    def send_broadcast(self, name):
        res = []
        broadcast = self.broadcast_devices(name)
        for b in broadcast.items():
            send_msg = { 
                    'type': 'mqtt.send',
                    'dev_type': 'dumb',
                    # send broadcast instead of name is actually is good idea
                    'uid': b[0],  
                    'command': 'CUP',
                    'task_id': '12345',
                    'payload': json.dumps({'config': b[1]})
            }
            # send broadcast instead of name is actually is good idea
            res.append(send_msg)
        for message in res:
            logger.debug(f'sending {message}')
            async_to_sync(channel_layer.send)('mqtts', message)
    
    def send_unicast(self):
        res = []
        unicast = self.unicast_devices()
        if not unicast:
            logging.warning('no smart devices is online') 
            return
        for dt in unicast.items():
            devices = dt[1]
            # sending update message to every device in receivers list
            for device in devices:
                send_msg = { 
                    'type': 'server.event',
                    'dev_type': dt[0],
                    'uid': device.uid
                }
                res.append(send_msg)
        for message in res:
            logger.debug(f'sending {res}')
            async_to_sync(channel_layer.send)('events', message)

    def change_value(self, alert, comment='new value'):
        value = self.value + int(alert)
        new_value = Value.objects.create(value=value,
                                         comment=comment)
        logging.info('changed alert value to {}'.format(new_value))
        new_value.save()
        self.state_based_on_value(new_value) 

    def __enter__(self):
        return self

    def __exit__(self, *err):
        return

    def __repr__(self):
        return 'GlobalStateManager context'
