FROM nginxinc/nginx-unprivileged:1-alpine

COPY ./default.conf.tpl /etc/nginx/default.conf.tpl

USER root

RUN mkdir -p /static /media \
    && chmod -R 755 /static /media \
    && touch /etc/nginx/conf.d/default.conf \
    && chown nginx:nginx /etc/nginx/conf.d/default.conf

USER nginx
