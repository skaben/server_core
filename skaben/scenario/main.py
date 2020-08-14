from alert.services import AlertService
from core.helpers import fix_database_conn


class Scenario:

    """ Default scenario """

    def new(self, data):
        # fixme: temporarily testing
        try:
            if not isinstance(data, dict):
                raise Exception(f"not a dict: {data}")

            datahold = data.get("datahold")

            if not datahold:
                raise Exception(f"{data} missing datahold")
            else:
                self.apply(datahold)

        except Exception as e:
            raise Exception(f"scenario cannot be applied to packet data: {data} \n reason: {e}")

    @fix_database_conn
    def apply(self, data):
        try:
            if data.get("alert") == "reset":
                with AlertService() as manager:
                    manager.set_state_by_name("green")
            else:
                with AlertService() as manager:
                    manager.set_state_by_name("yellow")
        except Exception as e:
            raise Exception(f"error when applying scenario {e}")


scenario = Scenario()

