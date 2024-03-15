FROM nginxinc/nginx-unprivileged:1-alpine

COPY ./default.conf.tpl /etc/nginx/default.conf.tpl
COPY uwsgi_params /etc/nginx/uwsgi_params
COPY ./run.sh /run.sh

ENV LISTEN_PORT=80
ENV APP_HOST=api
ENV APP_PORT=8000

USER root

RUN mkdir -p /static /media \
    && chmod -R 755 /static /media \
    && touch /etc/nginx/conf.d/default.conf \
    && chown nginx:nginx /etc/nginx/conf.d/default.conf \
    && chmod +x /run.sh

USER nginx

CMD ["/run.sh"]
