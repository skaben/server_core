import time
import json
#from sk_rest import urls as REST
from sk_rest import models as API
from django.conf import settings

# TODO: make your own rest api

#serializers = {
#    'lock': REST.LockSerializer,
#    'terminal': REST.TerminalSerializer,
#}


class EventContext:

    """
        basic context manager methods
    """

    nosend_fields = ['descr', '_state', 'id', 'term_id_id']

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
        event.pop('type', None)  # remove channel_layer info

        self.old = None
        self.event = event  # maybe later
        try:
            self.model = self.model_list.get(event['dev_type'], None)
        except KeyError:
            raise Exception(f'no such model: {event["dev_type"]}')

        self.__dict__.update(event)
        self.ts = event['payload']['ts']
        #timeout = 2  # TEST purposes TODO: get from config

        if self.ts + settings.APPCFG.get('timeout', 30) < int(time.time()):
            self.old = True

    def get_conf(self, fields=None):
        if not self.qs:
            self.get()
        db_data = {k: v for k, v in self.qs.__dict__.items()
                   if k not in self.nosend_fields}
        try:
            if not fields:
                # just put all config in it
                pl = db_data
            else:
                # here comes filtering
                pl = {k: v for k, v in db_data.items() if k in fields}
            payload = json.dumps(pl).replace("'", '"')
        except ValueError:
            # bad fields
            raise
        except:
            # something else went wrong
            raise
        return payload

    def mqtt_response(self):
        mqtt_response = {
            'dev_type': self.event['dev_type'],
            'dev_id': self.event['dev_id'],
            'payload': self.get_conf()
        }
        return mqtt_response

    def get(self):
        M = self.model_list.get(self.dev_type, None)
        assert M, \
            Exception(f'unknown model type for {self.dev_type}')
        self.qs = M.objects.get(id=int(self.dev_id))
        return self.qs

    def __repr__(self):
        return f"this is device context with {self}, old: {self.old}"