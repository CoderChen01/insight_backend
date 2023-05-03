#!/bin/bash
python3 manage.py makemigrations \
    && python3 manage.py migrate \
    && celery -A insight worker -D \
       -P gevent -c 100 -l info \
       --pidfile="/var/run/worker.pid" --logfile="worker.log" \
    && celery -A insight beat --detach -l info \
       --scheduler django_celery_beat.schedulers:DatabaseScheduler \
       --pidfile="/var/run/beat.pid" --logfile="beat.log" \
    && uwsgi --ini uwsgi.ini
