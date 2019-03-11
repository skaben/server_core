import time
from .helpers import pl_decode, pl_encode, sjoin


class BasePacket:
    """
        Base packet class
    """
    def __init__(self, dev_type, dev_name=None):
        self.data = dict()  # packet payload
        self.command = str()  # command, assign in child classes
        self.ts = int(time.time())  # timestamp on start
        self.dev_type = dev_type  # group channel address

        # WARNING: dev_name here will be used for addressing.
        # for any other purposes, you should pass device name with 'data'
        self.dev_name = dev_name  # personal channel address, optional

    def encode(self):
        if self.dev_name:
            # unicast, send by name
            topic = sjoin((self.dev_type, str(self.dev_name)))
        else:
            topic = self.dev_type
        self.data.update({'ts': self.ts})
        data = pl_encode(self.data)
        payload = sjoin((self.command, data))
        return tuple((topic, payload))

    def __repr__(self):
        if self.dev_name:
            return f'<{self.command}>\t{self.dev_type}/{self.dev_name}\t{self.ts}'
        else:
            return f'<{self.command}>\t{self.dev_type}\t{self.ts}'

# actual packets


class ACK(BasePacket):
    """
        Confirm previous packet as success
        Should send ts of previous packet
    """
    def __init__(self, dev_type, task_id, dev_name=None):
        super().__init__(dev_type, dev_name)
        self.command = 'ACK'
        self.task_id = task_id


class NACK(BasePacket):
    """
        Confirm previous packet as unsuccess
        Should send ts of previous packet
    """
    def __init__(self, dev_type, task_id, dev_name=None):
        super().__init__(dev_type, dev_name)
        self.command = 'NACK'
        self.task_id = task_id


class WAIT(BasePacket):
    """
        Sent in response of PONG, currently
        before sending another PONG client should either
        wait timeout or receive nowait-packet (CUP/SUP)
    """
    def __init__(self, dev_type, timeout, dev_name=None):
        super().__init__(dev_type, dev_name)
        if isinstance(timeout, float):
            timeout = int(timeout)

        if not isinstance(timeout, int):
            try:
                timeout = round(int(timeout))
            except Exception:
                raise ValueError(f'bad timeout value: {timeout}')
        self.command = 'WAIT'
        self.data['timeout'] = timeout


class PING(BasePacket):
    """
        Ping packet. Broadcast only.
    """
    def __init__(self, dev_type):
        super().__init__(dev_type)
        self.command = 'PING'


class PONG(BasePacket):
    """
        PONG packet, send only in response to PING
        Should send timestamp value of PING
    """
    def __init__(self, dev_type, dev_name, ts):
        super().__init__(dev_type, dev_name)
        self.command = 'PONG'
        self.ts = ts

# packets with payload

class PayloadPacket(BasePacket):
    """
        Loaded packet basic class.
    """
    def __init__(self, dev_type, payload, dev_name=None):
        super().__init__(dev_type, dev_name)
        if isinstance(payload, str):
            try:
                payload = pl_decode(payload)
            except:
                raise Exception(f'cannot decode {payload}')
        self.data.update(**payload)


class CUP(PayloadPacket):
    """
        Client UPdate - update client config
    """
    def __init__(self, dev_type, payload, dev_name=None):
        super().__init__(dev_type, payload, dev_name)
        self.command = 'CUP'


class SUP(PayloadPacket):
    """
        Server UPdate - update server config
    """
    def __init__(self, dev_type, payload, dev_name=None):
        super().__init__(dev_type, payload, dev_name)
        self.command = 'SUP'

