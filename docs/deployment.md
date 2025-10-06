# Развертывание проекта

---

- Требования
    - Docker engine
    - docker-compose
    - make

**Основной репозиторий проекта:**

https://github.com/skaben/skaben

(это не монорепозиторий, проект развертывается с помощью git submodules)

### Win + WSL:

[Docker Desktop WSL 2 backend on Windows](https://docs.docker.com/desktop/windows/wsl/)

### Linux:

[Install Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)

<aside>
🟠 РЕКОМЕНДАЦИЯ: используемое для разработки IDE - любое, которое хорошо работает с WSL и Докером (Бес рекомендует [VSCode](https://code.visualstudio.com/), который умеет это все в бесплатной версии и очень хорошо)

</aside>

<aside>
🔴 ВНИМАНИЕ: для использования в production (управления данжом) нужно помнить о необходимости настроить файрволл чтобы порты, используемые сборкой, были доступны из сети данжа.

</aside>

<aside>
🔴 ВНИМАНИЕ: сборка отправлялась в production только на машине под управлением Linux (Ubuntu 18, 20 LTS). Используйте Win-server на игре на ваш страх и риск.

</aside>

### запуск сборки TL;DR

---

1. склонить себе основной репозиторий https://github.com/skaben/skaben
2. сказать `make fetch`
3. положить `.env` в `skaben/server_core`
4. сказать `make build && make start`
5. не забыть создать суперпользователя Django `make superuser`
6. создать и применить миграции БД через `make migrations && make migrate`

<aside>
🟢 для удобства руления докером автоматически стартует **Portainer** - доступен на `127.0.0.1:9000` с логином-паролем `skaben: portainerpasswd`

[доступ к стеку по ссылке](http://127.0.0.1:9000/#!/2/docker/stacks/skaben?type=2&regular=false&external=true&orphaned=false)

</aside>

### содержимое .env

```bash
ENVIRONMENT='testing'
DB_HOST='db'
DB_NAME='skaben'
DB_USER='skaben'
DB_PASS='sk4b3n'
POSTGRES_DB='skaben'
POSTGRES_USER='skaben'
POSTGRES_PASSWORD='sk4b3n'
RABBITMQ_ERLANG_COOKIE=''
RABBITMQ_USERNAME='mqtt'
RABBITMQ_PASSWORD='skabent0mqtt'
```

### Где что работает и как запускается

---

- фронт запускается на `127.0.0.1`
- Django-админка на `127.0.0.1/admin`
- веб-интерфейс rabbitmq - `127.0.0.1:15672`

<aside>
🟢 попасть в **RabbitMQ** можно с парой логин-пароль `rabbitmq: rabbitmqpasswd`

</aside>

### Дополнительно можно поднять pgadmin:

---

- `cd docker_build/pgadmin && docker-compose up`
- он стартует на `127.0.0.1:5050` и требует минимальной настройки в веб-интерфейсе, чтобы подключиться к БД

Все операции со сборкой производятся через `make`, ниже приведен список команд. Запуск без аргументов показывает `help`.

### Команды (нужен установленный make)

---

`fetch:` Скачать все submodules (фронт и бэк)

`build:` Запустить сборку сервисов

`rebuild:` Собрать без кэша, с удалением node_modules

`start:` Запуск всех сервисов

`sh.%:` Открыть shell в указанном сервисе [sh.[service]]

`exec:` Выполнение команды в указанном сервисе [service [command]]
`migrate` Применить миграции

`migrations` Создать новую миграцию

`superuser` Создать суперюзера в админке Django

`stop` Остановка всех сервисов

`restart.%:` Перезапустить сервис [restart.[service]]

`info` Показать список сервисов