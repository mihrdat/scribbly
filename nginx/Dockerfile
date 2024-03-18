FROM nginxinc/nginx-unprivileged:1.24

COPY . /

USER root

RUN chmod +x /nginx-entrypoint.sh

USER nginx
