#!/bin/bash

echo "+---------------------------------------+"
echo "| Substituting environment variables... |"
echo "+---------------------------------------+"
envsubst '\$LISTEN_PORT \$UPSTREAM_HOST \$UPSTREAM_PORT' < /nginx.conf > /etc/nginx/conf.d/default.conf

echo "+-------------------+"
echo "| Starting nginx... |"
echo "+-------------------+"
nginx -g 'daemon off;'
