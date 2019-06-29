#!/bin/bash

EXTERNAL_IP_ADDR=$(dig +short myip.opendns.com @resolver1.opendns.com)
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -subj "/C=US/CN=$EXTERNAL_IP_ADDR" \
  -keyout /etc/ssl/private/self-signed.key -out /etc/ssl/certs/self-signed.crt
