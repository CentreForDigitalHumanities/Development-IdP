#!/bin/sh

# Migrate the database
python manage.py migrate

# Run da server
exec gunicorn testidp.wsgi:application -c gunicorn.conf.py "$@"