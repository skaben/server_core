import time
import json
import logging
from .models import Terminal, Lock, Dumb, Permission
from django.conf import settings

# TODO: make your own rest api

class EventContext:

    """
        Event Context is interface between decoded MQTT packet and database
        All operations with ORM are performed in this context
        Contains basic context manager methods
    """

    nosend_fields = ['descr',
                     '_state',
                     'ts',  # should be set by server time
                     'id',  # server-side id
                     'uid',  # no need
                     'online',  # only server need it
                     'override',  # only server need it
                     'ip',  # only server need it
                     'offline']  # virtual status

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
        if isinstance(self.qs, Terminal):
            self.nosend_fields.extend(['menu_normal', 'menu_hacked', 'lock_id'])
        elif isinstance(self.qs, Lock):
            self.nosend_fields.extend(['access_list'])
        payload = {k:v for (k,v) in data_from_db.items()
                           if k not in self.nosend_fields}
        return payload

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
        try:
            M = self.model_list.get(self.dev_type, None)
        except:
            raise Exception(f'unknown model type for {self.dev_type}')
        try:
            self.qs = M.objects.get(uid=self.uid)
        except M.DoesNotExist:
            # todo: user exception not built-in
            raise NameError
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

        self.ts = event.get('ts', 0)

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

