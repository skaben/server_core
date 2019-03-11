from .helpers import *
from .packets import *

CMD = {
        'PING': PING,  # heartbeat, broadcast
        'PONG': PONG,  # response to PING with PING timestamp
        'ACK': ACK,   # confirm success (to CUP/SUP)
        'NACK': NACK,  # confirm fail (to CUP/SUP)
        'WAIT': WAIT,  # device stop sending PONGs for a time
        'CUP': CUP,  # Client UPdate config from server
        'SUP': SUP  # Server UPdate config from client
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
        return json.dumps(self.data)


class PacketSender(BaseContext):
    """
        Packet context creates packets from packets
    """

    def __init__(self):
        super().__init__()
        self.cmd = CMD

    def create(self, packet_type, **kwargs):
        p = self.cmd.get(packet_type)
        self.packet = p(**kwargs)
        return self.packet


class PacketReceiver(BaseContext):
    """
        This context decodes information from MQTT packets
    """

    def __init__(self):
        super().__init__()

    # def decode(self, msg):
    #     if isinstance(msg, bytes):
    #         msg = msg.decode('utf-8')

    #     try:
    #         res = json.loads(msg.replace("'", '"'))
    #     except:
    #         raise Exception('cannot decode message')

    #     if res.get('payload', None):
    #         if isinstance(res['payload'], str):
    #             try:
    #                 res['payload'] = json.loads(res['payload'])
    #             except:
    #                 raise Exception('cannot decode payload')

    #     self.from_dict(res)
    #     return self.data


    def _check_args(self, arglist):
        for k in arglist:
            if not self.data.get(k, None):
                err = f'missing {k} from {self.data}'
                raise Exception(err)

    def _dtype(self, arg):
        """
            device type from message topic
        """
        if arg.endswith('ask'):
            arg = arg[:-3]
        return arg

    def _command(self, arg):
        """
            command from message payload
        """
        if arg not in CMD:
            raise Exception(f'unknown command: {cmd}')
        return arg

    def _payload(self, arg):
        if not arg:
            return
        try:
            pl = pl_decode(arg)
        except:
            raise Exception('received string from dumb device, deal with it')

        # optional fields parsing
        self.ts = pl.get('ts', 0)

        if self.data['command'] in (('ACK', 'NACK')):
            self.task_id = pl.get('task_id', None)
            if not self.task_id:
                raise Exception(f'missing task_id for {self}')
        # TODO: etc, check optional fields for other packets
        return pl

    def create(self, msg):
        """
            parse packet, make consistency checks
        """
        topic = safelist(msg.topic.split('/'))
        try:
            message = safelist(msg.payload.decode("utf-8").split('/'))
        except:
            print(f'cannot decode {msg}')
        # critical fields
        self.data['dev_type'] = self._dtype(topic.get(0, None))
        self.data['command'] = self._command(message.get(0, None))
        self.data['payload'] = self._payload(message.get(1, None))
        self._check_args(('dev_type', 'command', 'payload'))
        # optional fields
        self.data['dev_name'] = topic.get(1, None)

        return self.data

    def jsonify(self):
        try:
            return json.dumps(self.data)
        except:
            raise Exception('cannot encode data')
