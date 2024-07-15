#!/bin/bash

echo "+----------------------------------+"
echo "| Waiting for RabbitMQ to start... |"
echo "+----------------------------------+"
./wait-for-it.sh rabbitmq:5672

echo "+------------------------+"
echo "| Starting Celery Worker |"
echo "+------------------------+"
celery -A config worker --loglevel=INFO
