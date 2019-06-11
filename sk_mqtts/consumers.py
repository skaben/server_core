from .mqtts import server
import logging
from sk_mqtts.shared.contexts import PacketSender
from channels.consumer import SyncConsumer

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
                cmd = message.get('command')
                dev_type = message.get('dev_type')
                logger.debug(f'send to {uid} <{dev_type}>: {cmd}')
                with PacketSender() as sender:
                    message.pop('type', None)
                    cmd = message.pop('command')
                    packet = sender.create(cmd, **message)
                    server.publish(packet.encode())
        except:
            logger.exception(f'cannot send packet via MQTT send: {message}')

        






