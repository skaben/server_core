from actions.alert import AlertService, get_current
from alert.serializers import AlertStateSerializer
from core.helpers import fix_database_conn
from transport.rabbitmq import exchanges
from transport.interfaces import send_log, publish_without_producer

from .models import UserInput


def check_power_state(datahold: dict):
    """Меняем уровень тревоги в зависимости от статуса щитка"""
    power_state = datahold.get('powerstate')
    dispatch = {
        'AUX': 'cyan',
        'PWR': 'green'
    }
    with AlertService() as service:
        state = service.get_state_by_name(dispatch.get(power_state))
        if not state:
            raise Exception(f'no state {state}')
        update_data = {'current': True}
        serializer = AlertStateSerializer(instance=state, data=update_data)
        if serializer.is_valid():
            serializer.update(state, update_data)


def is_alert_reset(datahold: dict):
    if datahold.get("alert") == "reset":
        with AlertService() as service:
            service.change_alert_level(1)


def is_message_denied(datahold: dict):
    """Increase alert level by keywords"""
    current = get_current()
    msg = datahold.get('message', '')
    if 'denied' in msg or 'rejected' in msg or 'failed' in msg:
        if getattr(current, "threshold", 0) > 0:
            with AlertService() as service:
                service.change_alert_level()


def open_hold():
    send_log('OPENING HOLD!!!')
    command = {
        "datahold": {"STR": "1/1000/S", "RGB": "FF00FF/1000/0/S"}
    }
    kwargs = {
        "body": command,
        "exchange": exchanges.get('mqtt'),
        "routing_key": "hold.all.cup"
    }
    publish_without_producer(
        **kwargs
    )


class EventManager:

    """ Default scenario """

    def apply(self, data):
        try:
            if not isinstance(data, dict):
                raise Exception(f"not a dict: {data}")

            if not data.get("datahold"):
                raise Exception(f"{data} missing datahold")
            else:
                self.pipeline(data)

        except Exception as e:
            raise Exception(f"scenario cannot be applied to packet data: {data} \n reason: {e}")

    @fix_database_conn
    def pipeline(self, data: dict):
        try:
            datahold = data.get("datahold")
            if data.get('device_type') == 'pwr':
                return check_power_state(datahold)

            if datahold.get("success"):
                return open_hold()

            if datahold.get('alert'):
                is_alert_reset(datahold)
            else:
                is_message_denied(datahold)
        except Exception as e:
            raise Exception(f"error when applying scenario {e} for {data}")

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return

# event_manager = EventManager()
