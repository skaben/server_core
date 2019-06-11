import time
import logging
from .helpers import pl_decode, pl_encode, sjoin

# TODO: beautify client ts passing as argument

class BasePacket:
    """
        Base packet class
    """
    def __init__(self, dev_type, ts=int(time.time()), uid=None):
        self.data = dict()  # packet payload
        self.command = str()  # command, assign in child classes
        self.ts = int(time.time()) # timestamp on start, should be external if client
        self.dev_type = dev_type  # group channel address

        # WARNING: uid here will be used for addressing.
        # for any other purposes, you should pass device name with 'data'
        self.uid = uid  # personal channel address, optional

    def encode(self):
        if self.uid:
            # unicast, send by name
            topic = sjoin((self.dev_type, str(self.uid)))
        else:
            topic = self.dev_type
        self.data.update({'ts': self.ts})
        data = pl_encode(self.data)
        payload = sjoin((self.command, data))
        return tuple((topic, payload))

    def __repr__(self):
        if self.uid:
            return f'<{self.command}>\t{self.dev_type}/{self.uid}\t{self.ts}'
        else:
            return f'<{self.command}>\t{self.dev_type}\t{self.ts}'

# actual packets


class ACK(BasePacket):
    """
        Confirm previous packet as success
        Should send ts of previous packet
    """
    def __init__(self, dev_type, task_id, uid=None, ts=int(time.time())):
        super().__init__(dev_type=dev_type,
                         uid=uid,
                         ts=ts)
        self.command = 'ACK'
        self.task_id = task_id


class NACK(BasePacket):
    """
        Confirm previous packet as unsuccess
        Should send ts of previous packet
    """
    def __init__(self, dev_type, task_id, uid=None, ts=int(time.time())):
        super().__init__(dev_type=dev_type,
                         uid=uid,
                         ts=ts)
        self.command = 'NACK'
        self.task_id = task_id


class WAIT(BasePacket):
    """
        Sent in response of PONG, currently
        before sending another PONG client should either
        wait timeout or receive nowait-packet (CUP/SUP)
    """
    def __init__(self, dev_type, timeout, uid=None, ts=int(time.time())):
        super().__init__(dev_type=dev_type,
                         uid=uid,
                         ts=ts)

        if isinstance(timeout, float):
            timeout = int(timeout)

        if not isinstance(timeout, int):
            try:
                timeout = round(int(timeout))
            except Exception:
                raise ValueError(f'bad timeout value: {timeout}')
        self.command = 'WAIT'
        self.data['timeout'] = timeout


class PINGLegacy(BasePacket):
    """
        Ping packet. Broadcast only.
    """
    def __init__(self, dev_type, ts=int(time.time())):
        super().__init__(dev_type=dev_type,
                         ts=ts)
        self.command = '*/PING'


class PING(BasePacket):
    """
        Ping packet. Broadcast only.
    """
    def __init__(self, dev_type, ts=int(time.time())):
        super().__init__(dev_type=dev_type,
                         ts=ts)
        self.command = 'PING'


class PONG(BasePacket):
    """
        PONG packet, send only in response to PING
        Should send timestamp value of PING
    """
    def __init__(self, dev_type, uid, ts=int(time.time())):
        super().__init__(dev_type=dev_type,
                         uid=uid,
                         ts=ts)
        self.command = 'PONG'
        self.ts = ts

# packets with payload

class PayloadPacket(BasePacket):
    """
        Loaded packet basic class.
    """
    def __init__(self, dev_type, payload, task_id,
                 uid=None, ts=int(time.time())):
        super().__init__(dev_type=dev_type,
                         uid=uid,
                         ts=ts)
        if isinstance(payload, str):
            try:
                payload = pl_decode(payload)
            except:
                raise Exception(f'cannot decode {payload}')
        self.data.update({'task_id': str(task_id)})
        self.data.update(**payload)


# TODO: review UID for cup/sup packets, please mind broadcasts

class CUP(PayloadPacket):
    """
        Client UPdate - update client config
    """
    def __init__(self, dev_type, payload, task_id,
                 uid=None, ts=int(time.time())):
        super().__init__(dev_type=dev_type,
                         task_id=task_id,
                         uid=uid,
                         payload=payload,
                         ts=ts)
        self.command = 'CUP'


class SUP(PayloadPacket):
    """
        Server UPdate - update server config
    """
    def __init__(self, dev_type, payload, 
                 task_id=0,  # for server updates no confirmation needed
                 uid=None, ts=int(time.time())):
        super().__init__(dev_type=dev_type,
                         task_id=task_id,
                         uid=uid,
                         payload=payload,
                         ts=ts)
        self.command = 'SUP'

