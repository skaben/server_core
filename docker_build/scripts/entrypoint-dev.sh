#!/bin/sh

echo "Awaiting broker"
/wait-for-it.sh rabbitmq:5672

echo "Waiting for database"
python manage.py wait_for_db

echo "Collect static files"
python manage.py collectstatic --noinput --clear

echo "Run dev server"
python manage.py runserver 0.0.0.0:8000
