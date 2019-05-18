import json
import time
import logging
from datetime import datetime
from .event_contexts import DeviceEventContext, ServerEventContext
from asgiref.sync import async_to_sync
from channels.consumer import SyncConsumer, AsyncConsumer
from channels.layers import get_channel_layer

from .forms import LogRecordForm

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
        # DO NOT GENERATE mqtt response here
        # sending CUP in response to SUP is bad idea

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
                self._log_ws(f'[!] sending CUP')
                async_to_sync(channel_layer.send)('mqtts', response)
        except:
            logger.exception('exception while sending config to client device')
            raise

    def device_event(self, msg):
        """
        Device event manager
        :param msg: message from Redis-backed channel layer
        :return:
        """
        self._log_ws('{dev_type}: {uid} sending {command}'.format(**msg))
        # next - send command
        with DeviceEventContext(msg) as dev:
            # initialize event context with received message
            # trying to get ORM object (or adding new device)
            orm = dev.get()
            if not orm:
                # TODO: call new_device procedure
                pass
            # update timestamp anyway
            orm.ts = dev.payload.pop('ts')
            update_fields = ['ts',]
            if not orm.online:
                orm.online = True
                update_fields.append('online')
            orm.save(update_fields=update_fields)
            # sending update to front
            update_msg = {'name': dev.dev_type, 'id': orm.id}
            self._update_ws(update_msg)
            #logger.debug(update_msg)
            # managing event depends of command

            # TODO: refactor CUP/SUP sending
            try:
                # no matter what - if you're old,
                # you should get config from server first
                if dev.old:
                    dev.command = 'PONG'

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

                elif dev.command in ('ACK', 'NACK'):
                    # check for task_id
                    # put into separated high-priority channel
                    # ackmanager deal with it
                    pass

                elif dev.command == 'CUP':
                    # client should be updated
                    # get device config
                    # add task_id
                    # send packet to mqtt via channel_layer
                    # await for ack/nack with task_id in separate channel
                    # retry X times
                    # except: log and update device as offline
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

                elif dev.command == 'SUP':
                    # server should be updated
                    # get_device
                    # validate data
                    # log data
                    # save device
                    update_fields = []
                    for field in dev.payload.keys():
                        # ignoring task_id for SUP
                        if field == 'task_id':
                            continue
                        if not hasattr(orm, field):
                            logging.error(f'Ignoring bad column for {dev.dev_type} : {field}')
                        else:
                            db_value = orm.__dict__.get(field)
                            new_value = dev.payload[field]
                            if db_value != new_value:
                                #print(f'update to DB: {field} is {new_value}')
                                setattr(orm, field, new_value)
                                update_fields.append(field)
                    if update_fields:
                        orm.save(update_fields=update_fields)
                    # do not send response to mqtt via channel_layer - left unanswered 
                    # send update to web via websocket : DONE by signals
                else:
                    logging.error(f'command {dev} not implemented')
            except:
                logging.exception(f'exception while {dev.command}')
                self._log_ws(f'FAILED {dev.command} for {dev_type}/{uid}')


    def save_log_record(self, msg):
        if isinstance(msg, dict):
            message = json.dumps(msg)
        elif isinstance(msg, str):
            message = msg
        else:
            logger.error(f'bad type of msg for logging: {type(msg)}:\n{msg}')
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
        logging.debug('websocket disconnect')
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
        logging.debug(f'ws log received: {data}')
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

