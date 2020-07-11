from kombu import Queue
from transport.rabbitmq import exchanges

ASK_EXCHANGE = exchanges.get('ask')
LOG_EXCHANGE = exchanges.get('log')


# reply to pong
pong_queue = Queue('pong',
                   durable=False,
                   exchange=ASK_EXCHANGE,
                   routing_key='#.PONG')

# task delivery confirm
ack_queue = Queue('ack',
                  durable=False,
                  exchange=ASK_EXCHANGE,
                  routing_key='#.ACK')

nack_queue = Queue('nack',
                   durable=False,
                   exchange=ASK_EXCHANGE,
                   routing_key='#.NACK')

# queue for sending configs to client
cup_queue = Queue('cup',
                  durable=False,
                  exchange=ASK_EXCHANGE,
                  routing_key='#.CUP')

# server state updates
sup_queue = Queue('sup',
                  durable=False,
                  exchange=ASK_EXCHANGE,
                  routing_key='#.SUP')

info_queue = Queue('info',
                   durable=False,
                   exchange=ASK_EXCHANGE,
                   routing_key='#.INFO')

# declare queues for log exchange

log_queue = Queue("log_info",
                  durable=True,
                  exchange=LOG_EXCHANGE,
                  routing_key="info")

error_queue = Queue("log_error",
                    durable=True,
                    exchange=LOG_EXCHANGE,
                    routing_key="error")
