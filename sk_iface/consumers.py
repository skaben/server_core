from .event_contexts import DeviceEventContext
from channels.generic.websocket import JsonWebsocketConsumer


# TODO: move models here, get rid of rest


class EventConsumer(JsonWebsocketConsumer):
    """
        Receive and parse events
    """

    def device(self, msg):
        """
        Device event manager
        :param msg: message from Redis-backed channel layer
        :return:
        """
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


    def web(self, msg):
        print(f'received from web: {msg}')
