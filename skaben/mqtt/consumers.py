import logging
from channels.consumer import SyncConsumer
from mqtt.server import interface
import skabenproto as sk

logger = logging.getLogger('skaben.sk_mqtts')


class MQTTConsumer(SyncConsumer):

    def mqtt_start(self, request):
        try:
            result = {'data': interface.start()}
        except Exception as e:
            result = {'data': None, 'error': e}
        return result

    def mqtt_stop(self, request):
        try:
            result = {'data': interface.start()}
        except Exception as e:
            result = {'data': None, 'error': e}
        return result

    def mqtt_send(self, message):
        """

        :param message: json with dev_type, command, payload (uid is optional)
        :return:
        """
        try:
            if not message:
                raise Exception('missing message')
            uid = message.get('uid', 'brd')
            dev_type = message.get('dev_type')
            with sk.PacketEncoder() as encoder:
                message.pop('type')
                cmd = message.pop('command')
                packet = encoder.load(cmd, **message)
                encoded = encoder.encode(packet)
                result = interface.server.publish(encoded)  # {'data': 'ok'}
            logger.debug(f'send to {uid} <{dev_type}>: {cmd}')
        except Exception as e:
            logger.exception("failed to send message:")
            result = {"error": f"{e}"}
        return result
