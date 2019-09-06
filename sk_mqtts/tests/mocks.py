from sk_mqtts.mqtts import MQTTServer
from multiprocessing import Queue

from django.conf import settings

import skabenproto as sk

q = Queue()
config = settings.APPCFG

class Server(MQTTServer):

    def __init__(self, config, queue):
        super().__init__(config, queue)
        pass

    def publish(self, message):
        return message

    def send_event(self, event):
        return event

server = Server(config, q)

def mock_message(dev_type='lock',
                 uid='00ff00ff00ff',
                 command='PING',
                 payload='{"data": "data"}'):

    class Message():
        def __init__(self, dev_type, uid, command, payload):
            self.topic = '/'.join((dev_type, uid))
            self.payload = bytes('/'.join((command, payload)), 'utf-8')

    msg = Message(dev_type, uid, command, payload)
    with sk.PacketDecoder() as decoder:
        e = decoder.decode(msg)


    return msg
