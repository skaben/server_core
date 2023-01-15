from core.reactions._old_scenario.base import BaseScenario


class Scenario(BaseScenario):

    DISPATCH_POWER_TABLE = {
        'AUX': 'cyan',
        'PWR': 'green'
    }

    def pipeline(self, data: dict):
        device_type = data.get('device_type')
        datahold = data.get('datahold')

        if device_type == 'pwr':
            return self.check_power_state(datahold.get('powerstate'))

        if device_type == 'terminal':
            if datahold.get('type') == 'hack' and not datahold.get('success'):
                self.alert_level_raise()

        if device_type == 'lock':
            if datahold.get('access') and not datahold.get('success'):
                self.alert_level_raise()

    def open_hold(self):
        """Осталось со Сталкера, держим примера ради"""
        payload = {'datahold': {'STR': '1/1000/S', 'RGB': 'FF00FF/1000/0/S'}}
        self.send_command_mqtt(
            topic="hold.all.cup",
            payload=payload
        )

