import json
import time
import logging
from datetime import datetime
from asgiref.sync import async_to_sync
from channels.consumer import SyncConsumer, AsyncConsumer
from channels.layers import get_channel_layer

channel_layer = get_channel_layer()
logger = logging.getLogger()


class EventConsumer(SyncConsumer):
    """
        Receive and parse events
    """
    groups = ['ws_send']

    def connect(self):
        self.channel_layer.group_add("ws_send", self.channel_name)

    def disconnect(self, close_code):
        self.channel_layer.group_discard("ws_send", self.channel_name)

    def send_to_ws(self, data=None):
        if not data:
            return
        msg = {
            'type': 'ws.update',
            'content': data
        }
        async_to_sync(self.channel_layer.group_send)('ws_send', msg)


class WebSocketConsumer(AsyncConsumer):

    channel_layer_alias = "default"
    groups = ["ws_send"]

    async def connect(self, event):
        await self.channel_layer.group_add("ws_send", self.channel_name)
        await self.send({
            "type": "websocket.accept",
        })

    async def disconnect(self, event):
        logger.debug('websocket disconnect')
        await self.send({
            "type": "websocket.accept",
        })

    async def receive(self, event):
        await self.channel_layer.send('events', {
            "type": 'websocket.event',
            "data": event,
        })

    async def log(self, data):
        logger.debug(f'ws log received: {data}')
        timestamp = datetime.now().strftime('%X')
        data.update({'time': timestamp})
        text = json.dumps(data)
        await self.send({
            "type": "websocket.send",
            "text": text
        })

    async def update(self, data):
        await self.send({
            "type": "websocket.send",
            "text": json.dumps(data)
        })
