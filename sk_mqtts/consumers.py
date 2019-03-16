from .mqtts import server
from .contexts import PacketSender
from channels.consumer import SyncConsumer

class MQTTConsumer(SyncConsumer):

    def mqtt_start(self, request):
        try:
            if not server.disabled:
                raise RuntimeError('MQTT server already up and running')
            server.enable()
        except RuntimeError as e:
            print(e)

    def mqtt_stop(self, request):
        try:
            if server.disabled:
                raise RuntimeError('MQTT server already stopped')
            server.disable()
        except RuntimeError as e:
            print(e)

    def mqtt_send(self, message):
        """

        :param message: json with dev_type, command, payload (dev_id is optional)
        :return:
        """
        print('consumed:', message)
        if server.disabled:
            print('server not running. start server before sending message!')
            return False
        try:
            with PacketSender() as sender:
                message.pop('type', None)
                cmd = message.pop('command')
                packet = sender.create(cmd, **message)
                server.publish(packet.encode())
        except:
            raise





