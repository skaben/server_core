class SkabenMutator(object):

    """ Default _old_scenario """

    def apply(self, data: dict):
        raise NotImplementedError('use inherited classes')


    @staticmethod
    def send_command_mqtt(topic: str, payload: dict):
        raise NotImplementedError
        # kwargs = {
        #     'body': payload,
        #     'exchange': exchanges.get('mqtt'),
        #     'routing_key': topic
        # }
        # publish_without_producer(
        #     **kwargs
        # )

    @staticmethod
    def send_control_command(name: str):
        raise NotImplementedError
        # command = ControlCommand.objects.filter(name=name).first()
        # if not command:
        #     return
        #
        # if command.channel and command.payload:
        #     kwargs = {
        #         "body": command.payload,
        #         "exchange": command.exchange,
        #         "routing_key": command.rk
        #     }
        #     publish_without_producer(
        #         **kwargs
        #     )

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return
