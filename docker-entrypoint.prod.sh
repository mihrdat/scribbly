#!/bin/bash

echo "+------------------------------------+"
echo "| Waiting for PostgreSQL to start... |"
echo "+------------------------------------+"
./wait-for-it.sh db:5432

echo "+-----------------------+"
echo "| Migrating database... |"
echo "+-----------------------+"
python manage.py migrate

echo "+------------------------+"
echo "| Starting the server... |"
echo "+------------------------+"
gunicorn --bind 0.0.0.0:8000 config.wsgi

