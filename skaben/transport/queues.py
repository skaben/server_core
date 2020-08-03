from kombu import Queue
from transport.rabbitmq import exchanges

ASK_EXCHANGE = exchanges.get('ask')
LOG_EXCHANGE = exchanges.get('log')
MAIN_EXCHANGE = exchanges.get('internal')


# reply to pong
pong_queue = Queue('pong',
                   durable=False,
                   exchange=ASK_EXCHANGE,
                   routing_key='#.PONG')

# sending configs to client
cup_queue = Queue('cup',
                  durable=False,
                  exchange=ASK_EXCHANGE,
                  routing_key='#.CUP')

# receive updates from clients
sup_queue = Queue('sup',
                  durable=False,
                  exchange=ASK_EXCHANGE,
                  routing_key="#.SUP")

info_queue = Queue('info',
                  durable=False,
                  exchange=ASK_EXCHANGE,
                  routing_key="#.INFO")

# task confirm as susccess
ack_queue = Queue('ack',
                  durable=False,
                  exchange=ASK_EXCHANGE,
                  routing_key='#.ACK')

# task confirm as fail
nack_queue = Queue('nack',
                   durable=False,
                   exchange=ASK_EXCHANGE,
                   routing_key='#.NACK')

# internal exchange

# save payloads to DB
save_queue = Queue('save',
                  durable=False,
                  exchange=MAIN_EXCHANGE,
                  routing_key='save')

# log exchange

log_queue = Queue("log_info",
                  durable=True,
                  exchange=LOG_EXCHANGE,
                  routing_key="info")

error_queue = Queue("log_error",
                    durable=True,
                    exchange=LOG_EXCHANGE,
                    routing_key="error")
