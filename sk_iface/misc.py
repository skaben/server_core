import logging
from django.db import transaction
from .models import Lock, Terminal, Dumb, State, Value, DevConfig

logger = logging.getLogger('skaben.sk_iface')


class GlobalStateManager:

    playable = ['green', 'yellow', 'red']

    def __init__(self):
        self.locks = Lock.objects.all()
        self.terms = Terminal.objects.all()
        self.dumbs = Dumb.objects.all()
        self.states = State.objects.all()
        self.value = Value.objects.all().latest('id')

    def device_update_list(self):
        return {
            'lock': self.locks.filter(online=True),
            'term': self.terms.filter(online=True),
            'dumb': self.dumbs # no online for dumbs...
        }

    def set_state(self, name, manual=None):
        # normal procedure
        if hasattr(self, name):
            if name != 'white':
                # exclude all manual controlled device from updates
                self.locks = self.locks.exclude(override=True)
                self.terms = self.terms.exclude(override=True)
            if name in self.playable:
                if not manual:
                    return self.state_based_on_value()
                else:
                    self._reset_threshold(name)
                    self.state(name)
            else:
                return self.state(name)

    def state(self, name):
        logger.info(f'setting state: {name}')
        if hasattr(self, name):
            try:
                call = getattr(self, name)
                return call()
            except:
                raise

    def state_based_on_value(self):
        new_state = None
        for state in self.states:
            if self.value.value >= state.threshold:
                new_state = state
        if new_state:
            return self.state(new_state.name)

    def set_as_current(self, name):
        try:
            other_states = self.states.exclude(name=name)
            other_states.update(current=False)
            #logger.debug(other_states)
            new_state = self.states.filter(name=name)
            for state in new_state:
                state.current = True
                state.save()
            self._set_dumb_config(name)
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

    def _reset_threshold(self, name):
        threshold = self.states.filter(name=name).first().threshold
        new_val = Value.objects.create(value=threshold,
                                       comment='level change auto-reset')
        new_val.save()

    def _set_dumb_config(self, name):
        with transaction.atomic():
            dumb_conf = DevConfig.objects.filter(state_name=name).all()
            #config.filter(
            #    state_name=State.objects.filter(name=name),
            #    dev_subtype='rgb'
            #)
            for device in self.dumbs:
                # GET RID OF SUBTYPES, AAAA
                config = dumb_conf.filter(
                    dev_subtype=device.dev_subtype)\
                    .first()
                device.config = config.config
                device.save()

    def __enter__(self):
        return self

    def __exit__(self, *err):
        return

    def __repr__(self):
        return 'GlobalStateManager context'
