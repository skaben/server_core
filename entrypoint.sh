#!/bin/sh

echo "Awaiting broker"
/opt/app/wait-for-it.sh rabbitmq:5672

echo "Waiting for database"
python manage.py wait_for_db
python manage.py createcachetable

echo "Collect static files"
python manage.py collectstatic --noinput --clear

if [ ${ENVIRONMENT} != 'dev' ]; then
    echo "Apply database migrations"
    python manage.py migrate
    echo "Run production server"
    gunicorn -b 0.0.0.0:8000 skaben.wsgi
else
    echo "Run dev server"
    python manage.py runserver 0.0.0.0:8000
fi
