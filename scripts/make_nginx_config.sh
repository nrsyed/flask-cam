#!/bin/bash

set -e

# Where this script lives, i.e., flask-cam/scripts
SCRIPTS_DIR=$(readlink -f $(dirname "$0"))

# Main application directory one level above this one.
APP_DIR=$(readlink -f "$SCRIPTS_DIR/..")

PORT=""
UNINSTALL=false

while (( $# > 0 )); do
  case "$1" in
    --port)
      PORT="$2"
      shift 2
      ;;
    uninstall)
      UNINSTALL=true
      shift 1
      ;;
    *)
      shift 1
      ;;
  esac
done

if $UNINSTALL; then
  # Determine port from nginx config file.
  PORT=$(grep listen /etc/nginx/sites-available/flaskcam | egrep -o '[0-9]+')
  sudo ufw delete allow $PORT
  [[ ! -f /etc/nginx/sites-enabled/flaskcam ]] || sudo rm /etc/nginx/sites-enabled/flaskcam
  [[ ! -f /etc/nginx/sites-available/flaskcam ]] || sudo rm /etc/nginx/sites-available/flaskcam
  [[ ! -f /etc/nginx/snippets/self-signed.conf ]] || sudo rm /etc/nginx/snippets/self-signed.conf
  [[ ! -f /etc/nginx/snippets/ssl-params.conf ]] || sudo rm /etc/nginx/snippets/ssl-params.conf
  [[ ! -f /etc/ssl/private/self-signed.key ]] || sudo rm /etc/ssl/private/self-signed.key
  [[ ! -f /etc/ssl/certs/self-signed.crt ]] || sudo rm /etc/ssl/certs/self-signed.crt
  [[ ! -f /etc/ssl/certs/dhparam.pem ]] || sudo rm /etc/ssl/certs/dhparam.pem
  exit 0
fi

if [[ -z "$PORT" ]]; then
  echo "Error: port required (use --port)"
  exit 1
fi

# Generate a self-signed SSL key and certificate, and Diffie-Helman group.
EXTERNAL_IP_ADDR=$(dig +short myip.opendns.com @resolver1.opendns.com)
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -subj "/C=US/CN=$EXTERNAL_IP_ADDR" \
  -keyout /etc/ssl/private/self-signed.key -out /etc/ssl/certs/self-signed.crt
sudo openssl dhparam -dsaparam -out /etc/ssl/certs/dhparam.pem 2048

# Addresses in the private IP space begin with one of three blocks:
# 10.X.X.X
# 172.16.X.X - 172.31.X.X
# 192.168.X.X
# This grep regex parses the output of ifconfig to programmatically obtain
# the local IP address, and takes into account different versions of ifconfig,
# some of which output `inet 192.168.X.X` and others `inet addr:192.168.X.X`.
REGEX='inet [a-zA-Z\:]*(192\.168|10\.[0-9]+|172\.1[6789]|172\.2[0-9]|172\.3[01])\.[0-9]+\.[0-9]+'
LOCAL_IP_ADDR=$(ifconfig | egrep -o "$REGEX" | egrep -o '[0-9]+.*[0-9]+')

# Create nginx config snippet pointing to SSL key and certificate.
echo "ssl_certificate /etc/ssl/certs/self-signed.crt;
ssl_certificate_key /etc/ssl/private/self-signed.key;" \
  | sudo tee /etc/nginx/snippets/self-signed.conf > /dev/null

# Generate ssl-params.conf based on settings from: https://cipherli.st,
# https://raymii.org/s/tutorials/Strong_SSL_Security_On_nginx.html, and
# https://digitalocean.com/community/tutorials/how-to-create-a-self-signed-ssl-certificate-for-nginx-on-debian-8
echo "ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
ssl_prefer_server_ciphers on;
ssl_ciphers \"EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH\";
ssl_ecdh_curve secp384r1;
ssl_session_cache shared:SSL:10m;
ssl_session_tickets off;
ssl_stapling on;
ssl_stapling_verify on;
resolver 8.8.8.8 8.8.4.4 valid=300s;
resolver_timeout 5s;
add_header Strict-Transport-Security \"max-age=63072000; includeSubdomains\";
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
ssl_dhparam /etc/ssl/certs/dhparam.pem;" \
  | sudo tee /etc/nginx/snippets/ssl-params.conf > /dev/null

# Create nginx config file, allowing only HTTPS access.
echo "server {
    listen $PORT ssl;
    server_name $LOCAL_IP_ADDR;
    include snippets/self-signed.conf;
    include snippets/ssl-params.conf;

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
