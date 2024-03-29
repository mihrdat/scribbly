FROM python:3.9.15

RUN pip install --upgrade pip

WORKDIR /app

COPY /requirements/common.txt /requirements/prod.txt /requirements/

RUN pip install --no-cache-dir -r /requirements/prod.txt

COPY . /app

RUN chmod +x /app/docker-entrypoint.sh && \
    chmod +x /app/wait-for-it.sh
