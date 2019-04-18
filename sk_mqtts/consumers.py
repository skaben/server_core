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
            logging.exception('[EXCEPTION]')

    def mqtt_stop(self, request):
        try:
            if not server.running:
                raise RuntimeError('MQTT server already stopped')
            server.stop()
        except RuntimeError as e:
            logging.exception('[EXCEPTION]')

    def mqtt_send(self, message):
        """

        :param message: json with dev_type, command, payload (dev_id is optional)
        :return:
        """

        if not server.running:
            logging.warning('server not running. start server before sending message!')
            return False
        else:
            dev_id = message.get('dev_id', 'broadcast')
            logging.debug('snd: {command} to {dev_type} '.format(**message),
                          f'id: {dev_id}')
        try:
            with PacketSender() as sender:
                message.pop('type', None)
                cmd = message.pop('command')
                packet = sender.create(cmd, **message)
                server.publish(packet.encode())
        except:
            raise





