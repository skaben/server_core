from core.models import GameConfig

from core.helpers import fix_database_conn
from scenario.alert import AlertService


def is_alert(data: dict):
    if data.get("alert") == "reset":
        with AlertService() as manager:
            manager.set_state_by_name("green")


def is_message(message: dict):
    msg = data.get('message', '').split(' ')
    if len(msg) > 1 and msg[1] == 'denied':
        with AlertService() as service:
            service.change_alert_level()



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

    @fix_database_conn
    def pipeline(self, data: dict):
        try:
            if data.get('alert'):
                is_alert(data)
            else:
                is_message(data)
        except Exception as e:
            raise Exception(f"error when applying scenario {e}")


event_manager = EventManager()
