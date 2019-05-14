from .mqtts import server
import logging
from sk_mqtts.shared.contexts import PacketSender
from channels.consumer import SyncConsumer

class MQTTConsumer(SyncConsumer):

    def mqtt_start(self, request):
        try:
            if server.running:
                raise RuntimeError('MQTT server already up and running')
            server.start()
        except RuntimeError as e:
            logging.exception('[!]')

    def mqtt_stop(self, request):
        try:
            if not server.running:
                raise RuntimeError('MQTT server already stopped')
            server.stop()
        except RuntimeError as e:
            logging.exception('[!]')

    def mqtt_send(self, message):
        """

        :param message: json with dev_type, command, payload (uid is optional)
        :return:
        """

        if not server.running:
            logging.warning('server not running. start server before sending message!')
            return False
        else:
            uid = message.get('uid', 'broadcast')
            logging.debug('snd: {command} to {dev_type} '.format(**message),
                          f'id: {uid}')
        try:
            with PacketSender() as sender:
                message.pop('type', None)
                cmd = message.pop('command')
                packet = sender.create(cmd, **message)
                server.publish(packet.encode())
        except:
            raise





