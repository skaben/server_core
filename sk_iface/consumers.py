import json
import logging
from datetime import datetime
from .event_contexts import DeviceEventContext
from asgiref.sync import async_to_sync
from channels.consumer import SyncConsumer
from channels.consumer import AsyncConsumer
from channels.layers import get_channel_layer

# TODO: move models here, get rid of rest

channel_layer = get_channel_layer()

import os

#  helper is temporarily here, to be moved

class LogWriter:
    def __init__(self):
        self.fname = 'wslogging'
        if not os.path.exists(self.fname):
            with open(self.fname, 'w+') as fh:
                fh.write('')

    def write(self, str):
        with open(self.fname, 'w+') as fh:
            fh.write(str + '\n')

    def read(self, lines=None):
        with open(self.fname, 'r') as fh:
            data = fh.readlines()[::-1]

        if not lines:
            return data
        else:
            return data[:lines]

lw = LogWriter()

class AckManager:

    def open(self, task):
        # open new task_id
        task_id = task['data'].pop('task_id')
        task_data = json.dumps(task['data'])



class EventConsumer(SyncConsumer):
    """
        Receive and parse events
    """
    groups = ['ws_send']

    def connect(self):
        self.channel_layer.group_add("ws_send", self.channel_name)

    def disconnect(self, close_code):
        self.channel_layer.group_discard("ws_send", self.channel_name)

    def device(self, msg):
        """
        Device event manager
        :param msg: message from Redis-backed channel layer
        :return:
        """
        self._log_ws('{dev_type}: {dev_id} sending {command}'.format(**msg))
        # next - send command
        with DeviceEventContext(msg) as dev:
            # initialize event context with received message
            # trying to get ORM object (or adding new device)
            orm = dev.get()
            if not orm:
                # TODO: call new_device procedure
                pass
            # update timestamp first
            orm.ts = dev.payload['ts']

            if dev.command == 'PONG':
                if dev.old:
                    # return config
                    response = dev.mqtt_response()
                    response.update({
                        'type': 'mqtt.send',
                        'command': 'CUP',
                        'task_id': '12345'
                    })
                    # holy cow, that's stupid channels
                    self._log_ws('[!] sending configuration to '
                                 '{dev_type}/{dev_id}'.format(**msg))
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
                pass

            elif dev.command == 'SUP':
                # server should be updated
                # get_device
                # validate data
                # log data
                # save device
                # do not send response to mqtt via channel_layer - left unanswered
                # send update to web via websocket
                # except: log event
                pass
            else:
                logging.error(f'command {dev} not implemented')

    def _log_ws(self, data=None):
        """
            cross-connection with webeventconsumer for sending messages to weblog
        :param data:
        :return:
        """
        if not data:
            return
        msg = {
            "type": "ws.log",
            "data": data,
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
        #lw.write(text)
        await self.send({
            "type": "websocket.send",
            "text": text
        })

