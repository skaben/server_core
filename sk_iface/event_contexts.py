import time
import json
#from sk_rest import urls as REST
from sk_rest import models as API

# TODO: make your own rest api

#serializers = {
#    'lock': REST.LockSerializer,
#    'terminal': REST.TerminalSerializer,
#}


class EventContext:

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


class DeviceEventContext(EventContext):
    """
        DB-interaction
    """

    model_list = {
        'lock': API.Lock,
        'terminal': API.Terminal,
    }

    def __init__(self, event):
        super().__init__()
        timeout = 2
        event.pop('type', None)  # remove channel_layer info

        self.old = None
        self.event = event  # maybe later
        self.__dict__.update(event)
        self.ts = event['payload']['ts']
        if self.ts + timeout < int(time.time()):
            self.old = True

    def get_conf(self, fields):
        data = self.qs.__dict__
        packet = {
            'dev_type': data.pop('dev_type'),
            'dev_id': data.pop('dev_id'),
            # TODO: should be tested carefully
        }
        try:
            pl = {k: v for k, v in data.items if k in fields}
            packet['payload'] = json.dumps(pl).replace("'", '"')
        except ValueError:
            # bad fields
            raise
        except:
            # something else went wrong
            raise
        return packet


    def get(self):
        M = self.model_list.get(self.dev_type, None)
        assert M, \
            Exception(f'unknown model type for {self.dev_type}')
        self.qs = M.objects.filter(name=self.dev_id)[0]
        assert self.qs, \
            self.new_device()
        return self.qs

    def __repr__(self):
        return f"this is device context with {self}, old: {self.old}"