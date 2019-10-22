import random
import time

class Device:

    fields = list()
    payload = dict()

    def __init__(self, **kwargs):
        self.payload['ts'] = kwargs.get('ts', int(time.time()))
        self.payload['uid'] = kwargs.get('uid', self._rand_uid())
        self.payload['ip'] = kwargs.get('ip', self._rand_ip())
        self.payload['online'] = kwargs.get('online', False)
        self.payload['override'] = kwargs.get('override', False)

        for key in self.fields:
            val = kwargs.get(key)
            if val:
                self.payload[key] = val

        self.__dict__.update(self.payload)

    def _rand_uid(self):
        """ Generate random UID """
        uid = [format(random.randint(0, 255), '02x') for x in range(6)]
        return ''.join(uid)

    def _rand_ip(self):
        """ Generate random IP """
        ip = [format(random.randint(1, 254)) for x in range(4)]
        return '.'.join(ip)

    def get_payload(self, *args):
        """ Return JSON-compatible payload """
        if args:
            return [_ for _ in self.payload if _ in args]
        else:
            return self.payload


class LockDevice(Device):
    """ Generate parameters for Lock smart device """

    fields = ('sound', 'closed', 'blocked', 'timer')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class TerminalDevice(Device):
    """ Generate parameters for Terminal smart device """

    fields = ('powered', 'blocked', 'block_time', 'hacked',
              'hack_attempts', 'hack_difficulty')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


def device_factory(device_type, **kwargs):
    """ device factory wrapper """
    _d = {
        'term': TerminalDevice,
        'terminal': TerminalDevice,
        'lock': LockDevice
    }

    device = _d.get(device_type)(**kwargs)
    return device
