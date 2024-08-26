#!/bin/bash

echo "+------------------------------------+"
echo "| Waiting for PostgreSQL to start... |"
echo "+------------------------------------+"
./wait-for-it.sh db:5432

echo "+----------------------------+"
echo "| Collecting static files... |"
echo "+----------------------------+"
python manage.py collectstatic --noinput

echo "+-----------------------+"
echo "| Migrating database... |"
echo "+-----------------------+"
python manage.py migrate

echo "+-----------------------------+"
echo "| Starting the WSGI server... |"
echo "+-----------------------------+"
gunicorn --bind 0.0.0.0:8000 config.wsgi
