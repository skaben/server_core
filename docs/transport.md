# Транспорт в SKABEN
| описан в `core.transport`

Транспорт (связность между различными модулями сервера и внешними устройствами (периферийными устройствами или клиентами), управляемыми через MQTT) реализован через набор очередей в RabbitMQ и воркеров, которые стартуют в отдельных docker-контейнерах и являются паблишерами\подписчиками этих очередей.

Роутинг между очередями описан внутри кода воркеров.

[Документация по роутингу находится здесь](transport_and_events/routing.md)

#### Логически транспорт состоит из:

- очередь входящих MQTT-пакетов
- очередь исходящих MQTT-пакетов
- очередь внутренних событий
    - основной обработчик событий
    - отправка конфигурации клиентам
    - сохранение конфигурации клиентов

### Сообщения, Пакеты, События

#### Сообщения

Базовая сущность - сообщения внутри AMQP.\
Пересылаются как пара `message, body`
- `message.delivery_info` - содержит данные адресации
- `message.headers` - содержит опциональные мета-данные сообщения
- `body` содержит полезную нагрузку

Сообщения и Пакеты описанные ниже - являются частными случаями Сообщений.

#### Пакеты
| описаны в `core.transport.packets`

Используются для передачи информации от и к периферийным устройствам.\
Конвертируются в MQTT автоматически в exchange `mqtt`.
> Передаваемый Пакет не может содержать заголовков - только `routing_key` (он же `delivery_info`) и полезную нагрузку `body`.

Любой Пакет терминируется на соответствующем обработчике очереди:
- PING - в ask (сообщению добавляется заголовок со значением timestamp, который затем проверяется в роутере internal)
- INFO - в internal (превращаясь в Сообщение внутренней очереди)
- CUP - в client_update
- SUP - в state_update

Обратная отправка Пакета осуществляется через метод `core.transport.publisher.send_mqtt`

#### События
| базовое событие описано в `core.transport.events`

Описывают внутренние серверные взаимодействия, реакции и изменения состояния.

Отправка События осуществляется через метод `core.transport.publisher.send_event`

### Регулярные задачи
| описаны в `core.scheduler`

модуль `tasks` - описывает рутинные задачи \
модуль `service` - описывает сбор и запуск тасок

Scheduler запускается в одноименном контейнере, представляет собой один async loop. Синхронные задачи выполняются через `sync_to_async`.

### Управление созданием очередей, привязка воркеров
| описано в `core.transport.config`

Происходит при старте контейнеров воркеров через management команду Django (описано в `core.management.commands`)

В этом процессе создается очередь с определенным именем, привязывается к существующему exchange в RabbitMQ, и на очередь назначается обработчик.

Все обработчики очередей описаны в `core.worker_queue_handlers`

#### Основные используемые очереди и функции обработчиков:

##### Ask
| описан в `core.worker_queue_handlers.ask_mqtt_handler`

Обрабатывает входящие MQTT-пакеты, маркированные ask. в начале топика. RabbitMQ настроен таким образом, чтобы фильтровать такие события в отдельный exchange + очередь, где они обрабатываются воркером. MQTT пакет распаковывается, роутинг-ключ приводится к внутреннему формату (заменяются `/` на `.`).

Исходящие пакеты отправляются в очередь `internal`

##### State_update
| описан в `core.worker_queue_handlers.state_update`

Сохраняет конфигурацию от клиентов в БД. Simple-устройства игнорируются.

##### Client_update
| описан в `core.worker_queue_handlers.client_update`

Отправляет конфигурации из БД клиентам, включая simple-устройства.

##### Internal

Обрабатывает события, связанные с изменениями состояния конфигурации клиентов или состоянием сервера. Многие серверные операции (изменение уровня тревоги) - создают собственные события в этой очереди.

В этом же обработчике применяются дополнительные правила, путем дописывания инструкций в метод `handle_event` (см. Сообщения)

### Роутинг

Роутинг выполняется воркером `internal_worker`.

#### Настройка правил

> !! Важно не путать метки очередей с метками пакетов

Метки <b>пакетов</b> (`core.transport.packets.SkabenPacketTypes`) используются для определения типа данных, пришедших от внешних устройств и назначения топиков при отправке данных обратно в MQTT.

Когда данные из MQTT декодируются и попадают в internal обработчик - метка пакета отрывается, и в соответствии с правилами обработчика назначается метка очереди.

Метки <b>очередей</b> (`core.transport.config.SkabenQueue`) используются для внутреннего роутинга.