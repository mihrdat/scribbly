release: python manage.py migrate
web: gunicorn config.wsgi
worker: celery -A config worker