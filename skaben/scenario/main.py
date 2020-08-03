from alert.services import StateManager


class Scenario:

    """ Default scenario """

    def new(self, data):
        if data.get("blocked"):
            with StateManager() as manager:
                manager.apply("yellow")
        elif data.get("closed"):
            with StateManager() as manager:
                manager.apply("green")

    def __enter__(self):
        return self

    def __exit__(self, *err):
        return


scenario = Scenario()
