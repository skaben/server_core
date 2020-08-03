# from transport import interfaces


class Scenario:

    """ Default scenario """

    def new(self, data):
        print(data)

    def __enter__(self):
        return self

    def __exit__(self, *err):
        return

scenario = Scenario()
