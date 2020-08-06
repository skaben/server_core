from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from core.models import AlertState, Lock, Terminal, Simple
from device.services import save_devices
from transport.interfaces import send_plain


def new_alert_threshold_lg_current(level_name):
    current = AlertState.objects.filter(current=True).first()
    try:
        new = AlertState.objects.filter(name=level_name).first()
        if new.threshold > current.threshold:
            return True
    except Exception as e:
        raise Exception(f"Error when comparing alert levels: alert level with name {level_name}\nreason: {e}")


class AlertService:
    """ Global Alert State service """

    def __init__(self):
        alert = settings.APPCFG['alert']
        self._min_val = alert.get('ingame')
        self._max_val = alert.get('max')
        self.state_ranges = dict()

        ingame = [state for state in AlertState.objects.all().order_by("threshold")
                  if state.threshold in range(self._min_val, self._max_val)]

        self.states = dict(enumerate(ingame))

        for index, item in self.states.items():
            next = self.states.get(index + 1)
            next_threshold = getattr(next, 'threshold', self._max_val)
            self.state_ranges.update({index: [item.threshold, next_threshold]})

    def reset_counter_to_threshold(self, instance):
        data = {'value': instance.threshold,
                'comment': f'changed to {instance.name} by API call'}
        return data

    def get_state_by_alert(self, alert_value: int):
        try:
            alert_value = int(alert_value)
            for index, _range in self.state_ranges.items():
                if alert_value in range(*_range):
                    return self.states.get(index)
        except Exception:
            raise

    def set_state_by_name(self, name):
        try:
            instance = AlertState.objects.filter(name=name).first()
            self.set_state_current(instance)
        except ObjectDoesNotExist:
            raise

    def set_state_current(self, instance):
        try:
            if not instance.current:
                qs = AlertState.objects.filter(current=True)
                with StateManager() as manager:
                    manager.apply(instance.name, service=True)
                qs.update(current=False)
                instance.current = True
                instance.save()
        except ObjectDoesNotExist:
            pass
        finally:
            return instance

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return


class StateManager:
    """
        Reflect dungeon alert state to smart devices

        DRY violation for more obvious ruleset
    """

    indicator = "RGB.ce436600"

    standart_lock = dict(closed=True,
                         blocked=False)

    standart_term = dict(powered=False,
                         blocked=False,
                         hacked=False)

    def __init__(self):
        self.locks = Lock.objects.all()
        self.terms = Terminal.objects.all()
        self.simple = Simple.objects.all()

        # state changing from lower to upper or not?
        self.escalate = None

    def indicate(self, color):
        send_plain(self.indicator, color)

    def apply(self, level_name, service=None):
        """
            Changing global alert state
        """
        # todo: more subtle solution needed for direct calling restriction
        if not service:
            raise Exception("State Manager should not be called directly, use AlertService instead")

        try:
            call = getattr(self, level_name)
            self.escalate = new_alert_threshold_lg_current(level_name)
            if call and level_name != 'white':
                # exclude all manual controlled device from updates
                self.locks = self.locks.exclude(override=True)
                self.terms = self.terms.exclude(override=True)
            call()
        except Exception as e:
            self.indicate("255,0,255")
            raise Exception(f'cannot apply alert state {level_name}\nreason: {e}')

    def white(self):
        """
            WHITE: dungeon reset to start position
            doors are open, terminals are unlocked, all IED defused
        """
        self.indicate("255,255,255")

        lock_payload = dict(closed=False,
                            sound=False,
                            override=False,
                            blocked=False,
                            timer=10)

        term_payload = dict(powered=False,
                            override=False,
                            blocked=False,
                            hacked=False,
                            hack_difficulty=6,
                            hack_wordcount=16,
                            hack_chance=10,
                            hack_attempts=4)

        save_devices('lock', lock_payload, self.locks)
        #self.terms.update(**term_payload)

    def blue(self):
        """
            BLUE: power-off status

            game starting, most doors are closed, power source disabled
        """
        self.indicate("0,0,255")
        lock_payload = self.standart_lock
        term_payload = self.standart_term

        save_devices('lock', lock_payload, self.locks)
        #self.terms.update(**term_payload)

    def cyan(self):
        """
            CYAN: emergency power mode

            players solving power source quest
        """
        self.indicate("0,255,255")
        lock_payload = self.standart_lock
        term_payload = self.standart_term
        save_devices('lock', lock_payload, self.locks)
        #self.terms.update(**term_payload)

    def green(self):
        """
            GREEN: normal mode

            power source enabled, alert level not increased
        """
        self.indicate("0,255,0")

        lock_payload = self.standart_lock

        term_payload = dict(
                            powered=True,
                            blocked=False,
                            hacked=False,
                            hack_wordcount=16,
                            hack_attempts=4,
                            hack_difficulty=6
        )

        save_devices('lock', lock_payload, self.locks)
        #self.terms.update(**term_payload)

    def yellow(self):
        """
            YELLOW: alert level "warning"

            dungeon difficulty increased
        """
        self.indicate("255,255,0")
        lock_payload = self.standart_lock
        term_payload = dict(
                            powered=True,
                            hacked=False,
        )

        if not self.escalate:
            lock_payload.update({"blocked": False})
            term_payload.update({"blocked": False})

        save_devices('lock', lock_payload, self.locks)
        #self.terms.update(**term_payload)

    def red(self):
        """
            RED: alert level "danger"

            dungeon difficulty at maximum, most doors are locked
        """
        self.indicate("255,0,0")
        lock_payload = self.standart_lock
        term_payload = dict(
                            powered=True,
                            hacked=False,
        )

        if not self.escalate:
            lock_payload.update({"blocked": False})
            term_payload.update({"blocked": False})

        save_devices('lock', lock_payload, self.locks)
        #self.terms.update(**term_payload)

    def black(self):
        """
            BLACK: game over, manual control
        """
        self.indicate("0,0,0")
        lock_payload = dict(
                            closed=True,
                            sound=True,
                            blocked=True,
        )
        term_payload = dict(
                            powered=False,
                            blocked=True,
        )

        save_devices('lock', lock_payload, self.locks)
        #self.terms.update(**term_payload)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return
