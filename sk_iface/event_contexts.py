import time
from sk_rest import urls as API

# TODO: make your own rest api

serializers = {
    'lock': API.LockSerializer,
    'terminal': API.TerminalSerializer,
}


class BaseContext:

    """
        basic context manager methods
    """

    def __init__(self):
        self.data = dict()

    def __enter__(self):
        return self

    def __exit__(self, *err):
        return

    def __repr__(self):
        return 'this is context'


class DeviceEventContext(BaseContext):

    def __init__(self, event):
        super().__init__()
        event.pop('type', None)
        self.old = None
        timeout = 1
        self.event = event
        self.__dict__.update(event)
        self.ts = event['payload']['ts']
        if self.ts + timeout < int(time.time()):
            self.old = True

    def __repr__(self):
        return f"this is device context with {self}, old: {self.old}"
