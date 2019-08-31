import json
import time
import logging
from datetime import datetime
from sk_iface.event_contexts import DeviceEventContext, ServerEventContext
from sk_iface.state_manager import GlobalStateManager
from sk_iface.scenarios import parse_scenario
from asgiref.sync import async_to_sync
from channels.consumer import SyncConsumer, AsyncConsumer
from channels.layers import get_channel_layer

from sk_iface.forms import LogRecordForm

channel_layer = get_channel_layer()
logger = logging.getLogger('skaben.sk_iface')


class EventConsumer(SyncConsumer):
    """
        Receive and parse events
    """
    groups = ['ws_send']

    def connect(self):
        self.channel_layer.group_add("ws_send", self.channel_name)

    def disconnect(self, close_code):
        self.channel_layer.group_discard("ws_send", self.channel_name)

    def post_save(self, msg):
        # handling post_save events
        self._log_ws(f'post_save signal as {msg}')
        self._update_ws(msg)

    def server_event(self, msg):
        # sending CUP as separate method much better
        self._log_ws(f'server_event as {msg}')
        try:    
            # TODO: send only fields that were updated!
            with ServerEventContext(msg) as server:
                # response with device type, uid and config from DB
                response = server.mqtt_response()
                response.update({'type': 'mqtt.send',  # label as mqtt packet
                                 'command': 'CUP',  # client should be updated
                                 'task_id': '12345'}) # task id for flow management
                #self._log_ws(f'[!] sending CUP {response}')
                async_to_sync(channel_layer.send)('mqtts', response)
        except:
            logger.exception('exception while sending config to client device')
            raise

    def broadcast_event(self, msg):
        #logger.info('RECEIVED BROADCAST: {}'.format(msg))
        if msg.get('payload') == 'conf':
            with GlobalStateManager() as mgr:
                mgr.send_broadcast(mgr.current.name, msg.get('dev_type')) 
        if msg.get('dev_type') == 'pwr':
            cmd = msg.get('payload')
            if cmd == 'online':
                self._log_ws('POWER device online')
            elif cmd == 'aux':
                self._log_ws('AUXILIARY power enabled')
                with GlobalStateManager() as mgr:
                    mgr.set_state('cyan')
            elif cmd == 'pwr':
                self._log_ws('POWER RESTORED')
                # no manual=True, so state will be set by threshold 
                with GlobalStateManager() as mgr:
                    mgr.set_state('green')

    def device_event(self, msg):
        """
        Device event manager
        :param msg: message from Redis-backed channel layer
        :return:
        """
        # more verbosity needed!
        #if msg.get('command') != 'PONG':
        #    self._log_ws('{dev_type}: {uid} sending {command}'.format(**msg))
        # initialize event context with received message
        with DeviceEventContext(msg) as dev:
            #  updating timestamp first
            # trying to get ORM object (or adding new device)
            orm = dev.get()
            if not orm:
                # TODO: call new_device procedure
                logger.warning('no such device')
                return

            try:
                # no matter what - if you're old,
                # you should get config from server first
                if dev.old:
                    orm.ts = int(time.time()) # set timestamp to server time
                    dev.command = 'PONG'
                else:
                    orm.ts = dev.ts

                update_fields = ['ts',]

                if not orm.online:
                    orm.online = True
                    update_fields.append('online')
                orm.save(update_fields=update_fields)
                # sending update to front
                update_msg = {'name': dev.dev_type, 'id': orm.id}
                self._update_ws(update_msg)

                if dev.command in ('ACK', 'NACK'):
                    # check for task_id
                    # put into separated high-priority channel
                    # ackmanager deal with it
                    return

                if dev.command == 'PONG':
                    if dev.old:
                        # device outdated, sending config back
                        response = dev.mqtt_response()
                        response.update({
                            'type': 'mqtt.send',
                            'command': 'CUP',
                            'task_id': '12345' # todo: redis backed task storage
                        })
                        #####   !!!  self._update_ws(msg['dev_type'])
                        # holy cow, that's stupid channels
                        self._log_ws('[!] sending configuration to '
                                     '{dev_type}/{uid}'.format(**msg))
                        async_to_sync(channel_layer.send)('mqtts', response)

                elif dev.command == 'CUP':
                    response = dev.mqtt_response()
                    response.update({
                            'type': 'mqtt.send',
                            'command': 'CUP',
                            'task_id': '12345' # todo: redis backed task storage
                        })
                    self._log_ws('[!] sending configuration to '
                                     '{dev_type}/{uid}'.format(**msg))
                    async_to_sync(channel_layer.send)('mqtts', response)

                elif dev.command == 'SUP':
                    # server should be updated
                    update_fields = []
                    keys = list(dev.payload.keys())
                    logger.info(f'received SUP from {dev.dev_type}/{dev.uid}\n'
                                f'{dev.payload}')
                    for field in keys:
                        if field == 'task_id':
                            continue
                        if not hasattr(orm, field):
                            # no such field in related model, some BS arrived
                            #logger.error(f'Ignoring bad column for {dev.dev_type} : {field}')
                            continue
                        # managing alert level
                        if field == 'message':
                            result = parse_scenario(dev.payload[field], dev)
                            self._log_ws(result)
                            continue
                        else:
                            # update ORM field by field
                            db_value = getattr(orm, field)
                            new_value = dev.payload[field]
                            if db_value != new_value:
                                setattr(orm, field, new_value)
                                update_fields.append(field)
                    # and saving, finally, with update fields
                    if update_fields:
                        logger.debug(update_fields)
                        orm.save(update_fields=update_fields)
                else:
                    logger.error(f'command {dev} not implemented')
            except:
                logger.exception(f'exception while {dev.command}')
                # TODO: shorten device uids and provide hyperlinks 
                self._log_ws(f'FAILED {dev.command} for {dev.dev_type}/{dev.uid}')


    def save_log_record(self, msg):
        if isinstance(msg, dict):
            message = json.dumps(msg)
        elif isinstance(msg, str):
            message = msg
        else:
            logger.error(f'bad type of msg for logger: {type(msg)}:\n{msg}')
        try:
            log = LogRecordForm({'timestamp': int(time.time()),
                                 'message': message})
            log.save()
        except:
            logger.exception('exception with log record')

    def _log_ws(self, data=None):
        """
            cross-connection with webeventconsumer for sending messages to weblog
        :param data:
        :return:
        """
        if not data:
            return
        self.save_log_record(data)
        msg = {
            "type": "ws.log",
            "data": data,
        }
        async_to_sync(self.channel_layer.group_send)('ws_send', msg)

    def _update_ws(self, data=None):
        if not data:
            return
        msg = {
            'type': 'ws.update',
            'content': data
        }
        async_to_sync(self.channel_layer.group_send)('ws_send', msg)


class WebEventConsumer(AsyncConsumer):
    # WARNING: it's the channel_layer from settings, not from routing
    channel_layer_alias = "default"
    groups = ["ws_send"]

    async def websocket_connect(self, event):
        await self.channel_layer.group_add("ws_send", self.channel_name)
        await self.send({
            "type": "websocket.accept",
        })

    async def websocket_disconnect(self, event):
        logger.debug('websocket disconnect')
        await self.send({
            "type": "websocket.accept",
        })

    async def websocket_receive(self, event):
        await self.channel_layer.send('events', {
            "type": 'websocket.event',
            "data": event,
        })
#        await self.send({
#            "type": "websocket.send",
#            "text": event["text"],
#        })

    async def ws_log(self, data):
        logger.debug(f'ws log received: {data}')
        timestamp = datetime.now().strftime('%X')
        data.update({'time': timestamp})
        text = json.dumps(data)
        await self.send({
            "type": "websocket.send",
            "text": text
        })

    async def ws_update(self, data):
        # data is dev_type
        await self.send({
            "type": "websocket.send",
            "text": json.dumps(data)
        })

