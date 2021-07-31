#!/bin/sh

echo "Awaiting broker"
/wait-for-it.sh rabbitmq:5672

echo "Waiting for database"
python manage.py wait_for_db
python manage.py createcachetable

echo "Apply database migrations"
python manage.py migrate

echo "Collect static files"
python manage.py collectstatic --noinput --clear

echo "Run gunicorn"
gunicorn -b 0.0.0.0:8000 skaben.wsgi
