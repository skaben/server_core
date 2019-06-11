import time
import json
import logging
from .models import Terminal, Lock, Dumb, Permission
from django.conf import settings

# TODO: make your own rest api

class EventContext:

    """
        basic context manager methods
    """

    nosend_fields = ['descr',
                     '_state',
                     'id',
                     'uid',
                     'online',
                     'override',
                     'ip',
                     'offline']

    model_list = {
        'lock': Lock,
        'terminal': Terminal,
        'term': Terminal,
        'dumb': Dumb
    }

    def __init__(self):
        self.data = dict()
        self.event = None
        self.dev_type = None
        self.uid = None
        self.qs = None


    # todo: send_conf method
    # todo: save_local method

    def get_conf(self, fields=None):
        if not self.qs:
            self.get()
        data_from_db = self.qs.to_dict()
        logging.info(data_from_db)
        if isinstance(self.qs, Terminal):
            self.nosend_fields.extend(['menu_normal', 'menu_hacked', 'lock_id'])
        elif isinstance(self.qs, Lock):
            self.nosend_fields.extend(['access_list'])

        data_from_db = {k:v for (k,v) in data_from_db.items()
                        if k not in self.nosend_fields}
        return data_from_db

    def mqtt_response(self):
        try:
            mqtt_response = {
                'dev_type': self.dev_type,
                'uid': self.uid,
                'payload': self.get_conf()
            }
            return mqtt_response
        except:
            raise
            #raise Exception('bad mqtt response')

    def get(self):
        M = self.model_list.get(self.dev_type, None)
        assert M, \
            Exception(f'unknown model type for {self.dev_type}')
        self.qs = M.objects.get(uid=self.uid)
        # todo: add new device if not
        return self.qs

    def __enter__(self):
        return self

    def __exit__(self, *err):
        return

    def __repr__(self):
        return 'this is context'


class DeviceEventContext(EventContext):
    """
        Parse event and get model from DB
        Error handling should be here too
    """

    def __init__(self, event):
        super().__init__()

        self.old = None

        self.dev_type = event.get('dev_type')
        self.command = event.get('command')
        self.payload = event.get('payload')
        self.uid = event.get('uid')

        try:
            self.model = self.model_list.get(self.dev_type, None)
        except KeyError:
            raise Exception(f'no such model: {self.dev_type}')

        self.ts = self.payload.get('ts', 0)

        if self.ts + settings.APPCFG.get('alive', 60) < int(time.time()):
            self.old = True

    def __repr__(self):
        return f"this is device context with {self}, old: {self.old}"


class ServerEventContext(EventContext):

    """
        Simplified context for server-side events
    """

    def __init__(self, event):
        super().__init__()
        event.pop('type')
        self.dev_type = event.get('dev_type') 
        self.uid = event.get('uid')

