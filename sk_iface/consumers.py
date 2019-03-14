import time
from .event_contexts import DeviceEventContext
from channels.generic.websocket import JsonWebsocketConsumer
from sk_rest import models as API

# TODO: move models here, get rid of rest

mod = {
    'lock': API.Lock,
    'terminal': API.Terminal,
}

class EventConsumer(JsonWebsocketConsumer):
    """
        Receive and parse events
    """

    def device(self, msg):
        """
        Device event manager
        :param msg: message from Redis-backed channel layer
        :return:
        """
        with DeviceEventContext(msg) as dev:
            # initialize event context with received message
            M = mod.get(dev.dev_type)
            db = M.objects.filter(name=dev.dev_name)[0]
            if dev.old:
                # todo: make not proof-of-concept!
                db.ts = int(time.time())
                db.save()
            if dev.command == 'PONG':
                pass
            else:
                print(f'command {dev} not implemented')


    def web(self, msg):
        print(f'received from web: {msg}')



