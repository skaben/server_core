from core.helpers import fix_database_conn
from scenario.alert import AlertService


def reset_alert_to_normal():
    with AlertService() as manager:
        manager.set_state_by_name("green")


class Scenario:

    """ Default scenario """

    def apply(self, data):
        # fixme: temporarily testing
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
    def pipeline(self, data):
        try:
            if data.get("alert") == "reset":
                reset_alert_to_normal()
            else:
                with AlertService() as manager:
                    manager.set_state_by_name("yellow")
        except Exception as e:
            raise Exception(f"error when applying scenario {e}")


scenario = Scenario()

