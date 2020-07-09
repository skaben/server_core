def unicast_devices(self):
    locks = self.locks.filter(online=True).all()
    terms = self.terms.filter(online=True).all()

    return {
        'lock': locks,
        'term': terms,
    }


def broadcast_devices(self, name):
    broadcast = {}
    dumb_conf = DevConfig.objects.filter(state_name=name).all()
    if dumb_conf:
        for d in dumb_conf:
            # todo: refactor later for every device type
            # update with types
            broadcast.update({d.dev_subtype: d.config})
        return broadcast
    else:
        logger.error('no devices set for broadcast')


def send_broadcast(self, name, dev_type=None):
    res = []
    broadcast = self.broadcast_devices(name)
    for b in broadcast.items():
        if dev_type:
            if b[0] != dev_type:
                continue
        send_msg = {
            'type': 'mqtt.send',
            'dev_type': 'dumb',
            # send broadcast instead of name is actually is good idea
            'uid': b[0],
            'command': 'CUP',
            'task_id': '12345',
            # 'payload': {'config': b[1]},
            'payload': json.dumps({'config': b[1]})
        }
        # send broadcast instead of name is actually is good idea
        res.append(send_msg)
    for message in res:
        logger.debug(f'sending {message}')
        # async_to_sync(channel_layer.send)('mqtts', message)


def send_unicast(self):
    res = []
    unicast = self.unicast_devices()
    if not unicast:
        logging.warning('no smart devices is online')
        return
    for dt in unicast.items():
        devices = dt[1]
        # sending update message to every device in receivers list
        for device in devices:
            send_msg = {
                'type': 'server.event',
                'dev_type': dt[0],
                'uid': device.uid
            }
            res.append(send_msg)
    for message in res:
        logger.debug(f'sending {res}')
        # async_to_sync(channel_layer.send)('events', message)
