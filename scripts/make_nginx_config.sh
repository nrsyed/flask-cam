#!/bin/bash

set -e

# Where this script lives, i.e., flask-cam/scripts
SCRIPTS_DIR=$(readlink -f $(dirname "$0"))

# Main application directory one level above this one.
APP_DIR=$(readlink -f "$SCRIPTS_DIR/..")

# TODO: require port number as argument to script.
PORT=9001

# Addresses in the private IP space begin with one of three blocks:
# 10.X.X.X
# 172.16.X.X - 172.31.X.X
# 192.168.X.X
# This grep regex parses the output of ifconfig to programmatically obtain
# the local IP address, and takes into account different versions of ifconfig,
# some of which output `inet 192.168.X.X` and others `inet addr:192.168.X.X`.
REGEX='inet [a-zA-Z\:]*(192\.168|10\.[0-9]+|172\.1[6789]|172\.2[0-9]|172\.3[01])\.[0-9]+\.[0-9]+'
LOCAL_IP_ADDR=$(ifconfig | egrep -o "$REGEX" | egrep -o '[0-9]+.*[0-9]+')

echo "server {
    listen $PORT;
    server_name $LOCAL_IP_ADDR

    location / {
        include proxy_params;
        proxy_pass http://unix:$APP_DIR/flaskcam.sock;
    }
}" | sudo tee /etc/nginx/sites-available/flaskcam > /dev/null

# Add above configuration to nginx sites-enabled
sudo ln -s /etc/nginx/sites-available/flaskcam /etc/nginx/sites-enabled

# Test configuration file; this should return no issues.
sudo nginx -t

# Restart nginx.
sudo systemctl restart nginx

# Add port to ufw allowed ports.
sudo ufw allow $PORT
