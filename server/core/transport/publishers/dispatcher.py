from typing import Optional
# from transport.rabbitmq import exchanges
from alert.models import get_current
# from transport.interfaces import send_log, publish_without_producer

from core.helpers import fix_database_conn
# from core.models import ControlCommand
from actions.alert import AlertService
from alert.serializers import AlertStateSerializer


class BaseScenario:

    """ Default _old_scenario """

    DISPATCH_POWER_TABLE = {
        'AUX': '',
        'PWR': ''
    }

    @fix_database_conn
    def apply(self, data):
        if not isinstance(data, dict):
            raise ValueError(f"not a dict: {data}")
        if not data.get("datahold"):
            raise AttributeError(f"{data} missing datahold")
        else:
            self.pipeline(data)

    def pipeline(self, data: dict):
        raise NotImplementedError('use inherited classes')

    def check_power_state(self, power_state: str):
        """Меняем уровень тревоги в зависимости от статуса щитка"""
        dispatch = self.DISPATCH_POWER_TABLE
        with AlertService() as service:
            state = service.get_state_by_name(dispatch.get(power_state))
            if not state:
                raise Exception(f'no state for {power_state}')
            update_data = {'current': True}
            serializer = AlertStateSerializer(instance=state, data=update_data)
            if serializer.is_valid():
                serializer.update(state, update_data)

    @staticmethod
    def alert_reset(level: Optional[int] = 1):
        """Сбрасывает тревогу до указанного значения или минимального игрового значения"""
        with AlertService() as service:
            service.change_alert_level(level)

    @staticmethod
    def alert_level_raise():
        """Изменяет текущий уровень счетчика тревоги, если система в игровом статусе"""
        current = get_current()
        if getattr(current, "threshold", 0) > 0:
            with AlertService() as service:
                service.change_alert_level()

    @staticmethod
    def send_command_mqtt(topic: str, payload: dict):
        raise NotImplementedError
        # kwargs = {
        #     'body': payload,
        #     'exchange': exchanges.get('mqtt'),
        #     'routing_key': topic
        # }
        # publish_without_producer(
        #     **kwargs
        # )

    @staticmethod
    def send_control_command(name: str):
        raise NotImplementedError
        # command = ControlCommand.objects.filter(name=name).first()
        # if not command:
        #     return
        #
        # if command.channel and command.payload:
        #     kwargs = {
        #         "body": command.payload,
        #         "exchange": command.exchange,
        #         "routing_key": command.rk
        #     }
        #     publish_without_producer(
        #         **kwargs
        #     )

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return
