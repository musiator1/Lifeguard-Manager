#!/bin/bash

until nc -z -v -w30 db 5432; do
  sleep 1
done

python manage.py migrate

python manage.py collectstatic --noinput

python manage.py loaddata sample_data.json

exec gunicorn --bind 0.0.0.0:8000 lifeguard_manager.wsgi:application
