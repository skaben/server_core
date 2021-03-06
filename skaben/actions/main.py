from actions.alert import AlertService
from core.helpers import fix_database_conn
from transport.interfaces import publish_without_producer

from .models import UserInput


def is_alert_reset(datahold: dict):
    if datahold.get("alert") == "reset":
        with AlertService() as manager:
            manager.set_state_by_name("green")


def is_message_denied(datahold: dict):
    """Increase alert level by keywords"""
    msg = datahold.get('message').split(' ')
    if set(['denied', 'rejected']).issubset(msg):
        with AlertService() as service:
            service.change_alert_level()


def is_input_received(datahold: dict):
    user_input = datahold.get('require')
    if user_input:
        inputs = UserInput.objects.filter(require=user_input).all()
        for callback in [i.action for i in inputs]:
            callback()


class EventManager:

    """ Default scenario """

    def apply(self, data):
        try:
            if not isinstance(data, dict):
                raise Exception(f"not a dict: {data}")

            datahold = data.get("datahold")

            if not datahold:
                raise Exception(f"{data} missing datahold")
            else:
                self.pipeline(datahold)

        except Exception as e:
            raise Exception(f"scenario cannot be applied to packet data: {data} \n reason: {e}")

    # def apply_callback(self, callback: str):
    #     pass

    # @fix_database_conn
    # def pipeline(self, data: dict):
    #     try:
    #         if data.get('alert'):
    #             is_alert_reset(data)
    #         else:
    #             is_message_denied(data)
    #     except Exception as e:
    #         raise Exception(f"error when applying scenario {e}")


event_manager = EventManager()
