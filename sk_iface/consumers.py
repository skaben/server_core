import json
from datetime import datetime
from .event_contexts import DeviceEventContext
from asgiref.sync import async_to_sync
from channels.consumer import SyncConsumer
from channels.consumer import AsyncConsumer
from channels.layers import get_channel_layer

# TODO: move models here, get rid of rest

channel_layer = get_channel_layer()

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
        self._send_ws_log(msg)
        # next - send command
        with DeviceEventContext(msg) as dev:

            # initialize event context with received message
            if dev.old:
                # update timestamp first
                pass

            if dev.command == 'PONG':
                # check timestamp
                # update timestamp
                pass
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
                # send response to mqtt via channel_layer
                # send update to web via websocket
                # except: log event
                pass
            else:
                print(f'command {dev} not implemented')

    def _send_ws_log(self, data=None):
        """
            cross-connection with webeventconsumer for sending messages to weblog
        :param data:
        :return:
        """
        if not data:
            print('no data')
            return
        msg = {
            "type": "send.log",
            "data": data,
        }
        print('sending', msg['data'])
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
        print('websocket disconnect')
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

    async def send_log(self, data):
        timestamp = datetime.now().strftime('%X')
        data.update({'time': timestamp})
        await self.send({
            "type": "websocket.send",
            "text": str(data)
        })
