### Routing

Роутинг выполняется воркером `internal_worker`.

#### Настройка правил

> !! Важно не путать метки очередей с метками пакетов 

Метки <b>пакетов</b> (`core.transport.packets.SkabenPacketTypes`) используются для определения типа данных, пришедших от внешних устройств и назначения топиков при отправке данных обратно в MQTT.

Когда данные из MQTT декодируются и попадают в internal обработчик - метка пакета отрывается, и в соответствии с правилами обработчика назначается метка очереди.

Метки <b>очередей</b> (`core.transport.config.SkabenQueue`) используются для внутреннего роутинга.