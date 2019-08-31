import time
from .mqtts import server
import logging
from sk_mqtts.shared.contexts import PacketSender
from channels.consumer import SyncConsumer
import skabenproto as sk

logger = logging.getLogger('skaben.sk_mqtts')

class MQTTConsumer(SyncConsumer):

    def mqtt_start(self, request):
        try:
            if server.running:
                raise RuntimeError('MQTT server already up and running')
            server.start()
        except RuntimeError as e:
            logger.exception('[!]')

    def mqtt_stop(self, request):
        try:
            if not server.running:
                raise RuntimeError('MQTT server already stopped')
            server.stop()
        except RuntimeError as e:
            logger.exception('[!]')

    def mqtt_send(self, message):
        """

        :param message: json with dev_type, command, payload (uid is optional)
        :return:
        """
        try:
            if not server.running:
                logger.warning('server not running. start server before sending message!')
                return False
            else:
                uid = message.get('uid', 'brd')
                dev_type = message.get('dev_type')
                with sk.PacketEncoder() as encoder:
                    print(message)
                    message.pop('type')
                    cmd = message.pop('command')
                    packet = encoder.load(cmd, **message)
                    encoded = encoder.encode(packet)
                    print(encoded)
                    server.publish(encoded)

                logger.debug(f'send to {uid} <{dev_type}>: {cmd}')

                #with PacketSender() as sender:
                #    message.pop('type', None)
                #    cmd = message.pop('command')
                #    packet = sender.create(cmd, **message)
                #    server.publish(packet.encode())
        except:
            logger.exception(f'cannot send packet via MQTT send: {message}')

        






