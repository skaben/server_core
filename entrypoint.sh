#!/bin/sh

echo "Awaiting broker"
/wait-for-it.sh rabbitmq:5672

cd /skaben

echo "Waiting for database"
python manage.py wait_for_db
python manage.py createcachetable

echo "Collect static files"
python manage.py collectstatic --noinput --clear

if [ $ENVIRON != 'dev' ]; then
    echo "Apply database migrations"
    python manage.py migrate
    echo "Run production server"
    gunicorn -b $CORE_HOST:$CORE_PORT skaben.wsgi
else
    echo "Run dev server"
    python manage.py runserver $CORE_HOST:$CORE_PORT
fi
