import kombu

from kombu import Connection, Exchange
from django.conf import settings

connection = Connection(settings.AMQP_URL)
pool = connection.ChannelPool()

kombu.disable_insecure_serializers(allowed=['json'])


with pool.acquire(timeout=10) as channel:
    # main mqtt exchange, used mainly for messaging out.
    # note that all replies from clients starts with 'ask.' routing key goes to ask exchange
    mqtt_exchange = Exchange('mqtt', type='topic')
    bound_mqtt_exchange = mqtt_exchange(channel)

    # ask exchange collects all replies from client devices
    ask_exchange = Exchange('ask', type='topic')
    bound_ask_exchange = ask_exchange(channel)

    # separated websocket exchange
    ws_exchange = Exchange('websocket', type="topic")
    bound_ws_exchange = ws_exchange(channel)

    # logging exchange
    log_exchange = Exchange('log', type='direct')
    bound_log_exchange = log_exchange(channel)

    # note that is 'direct'-type
    # event_exchange serve as main internal server exchange, collecting all types of items
    events_exchange = Exchange('internal', type='direct')
    bound_events_exchange = events_exchange(channel)

    # declare exchanges
    for exchange in (bound_mqtt_exchange,
                     bound_events_exchange,
                     bound_ask_exchange,
                     bound_ws_exchange,
                     bound_log_exchange):
        exchange.declare()
    # binding ask exchange to mqtt exchange with routing key
    bound_ask_exchange.bind_to(exchange=bound_mqtt_exchange,
                               routing_key='ask.#',
                               channel=channel)

exchanges = {'ask': bound_ask_exchange,
             'internal': bound_events_exchange,
             'mqtt': bound_mqtt_exchange,
             'log': bound_log_exchange,
             'websocket': bound_ws_exchange}
