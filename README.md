##### skaben server rig

Сервер управления SKABEN

- база конфигураций клиентских устройств
- обработчик игровых событий
- управление глобальным состоянием игровой среды
- мониторинг

##### как запускать 
`docker-compose up --abort-on-container-exit
`

##### компоненты

- django (+ django-rest-framework)
- celery
- rabbitmq
- postgres
- nginx
