#!/bin/bash

echo "+---------------------------------------+"
echo "| Substituting environment variables... |"
echo "+---------------------------------------+"
envsubst < /etc/nginx/default.conf.tpl > /etc/nginx/conf.d/default.conf

echo "+------------------+"
echo "| Starting nginx...|"
echo "+------------------+"
nginx -g 'daemon off;'
