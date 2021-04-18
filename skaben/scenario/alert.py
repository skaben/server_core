from core.models import AlertState, Lock  # , SimpleLight #Terminal, Simple
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from scenario.device import send_config_all
from transport.interfaces import send_mqtt


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

    @staticmethod
    def reset_counter_to_threshold(instance):
        data = {'value': instance.threshold,
                'comment': f'changed to {instance.name} by API call'}
        return data

    @staticmethod
    def set_state_current(instance):
        try:
            if not instance.current:
                instance.current = True
                instance.save()
                send_config_all()
        except ObjectDoesNotExist:
            pass
        finally:
            return instance

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return