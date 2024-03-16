FROM python:3.9.15

RUN pip install --upgrade pip

WORKDIR /app

COPY /requirements/common.txt /requirements/dev.txt /requirements/

RUN pip install -r /requirements/dev.txt

COPY . /app

RUN chmod +x /app/docker-entrypoint.sh && \
    chmod +x /app/wait-for-it.sh
