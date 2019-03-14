import time
import json


class safelist(list):
    def get(self, index, default=None):
        try:
            return self.__getitem__(index)
        except IndexError:
            return default


def sjoin(strings):
    # join list with possible empty values
    return '/'.join(x.strip() for x in strings if x.strip())


def pl_encode(pl):
    # dict to str
    pl.pop('_sa_instance_state', None)
    return json.dumps(pl).replace("'", '"')


def pl_decode(pl):
    # str to dict
    return json.loads(pl.replace("'", '"'))


def cdl_retry(tries=1, 
              interval=1, 
              maxtime=None, 
              callback=None):
    # TODO: should be decorator
    if not callback or tries < 1 or interval < 1:
        raise Exception(f'bad parameters for retry'
                        f'{tries} {interval} {callback}')
    if maxtime:
        start_time = time.time()
        while True:
            res = callback() 
            if time.time() - start_time >= maxtime:
                raise Exception('timeout expired')
            if res:
                return res
            time.sleep(interval)
    else:
        for x in range(tries):
            res = callback()
            if res:
                return res
            time.sleep(interval)
    
"""
class Commands:

    ping = [
            'PING', # to client
            'PONG' # from client
    ]

    chconf = [
            'CUP', # Client UPdate, config push to client
            'SUP', # Server UPdate, config get from client
    ]

    system = [
            'CREATE',
            'DELETE',
            'UPDATE',
            'SELECT'
    ]

    ack = ['ACK', 'NACK']


command_list = Commands()    
"""