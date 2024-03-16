FROM nginxinc/nginxinc/nginx-unprivileged:1-alpine

COPY . /

USER root

RUN chmod +x /docker-entrypoint.sh

USER nginx
