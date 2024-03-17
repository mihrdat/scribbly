FROM python:alpine3.19

RUN pip install --upgrade pip

WORKDIR /app

COPY /requirements/common.txt /requirements/dev.txt /requirements/

RUN pip install -r /requirements/dev.txt

COPY . /app

RUN adduser --disabled-password --no-create-home appuser && \
    chmod +x /app/docker-entrypoint.sh && \
    chmod +x /app/wait-for-it.sh

USER appuser
