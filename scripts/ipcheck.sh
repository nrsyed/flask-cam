#!/bin/bash

# Where this script lives, i.e., the /scripts directory.
SCRIPTS_DIR=$(readlink -f $(dirname "$0"))

# Main application directory one level up from this one.
APP_DIR=$(readlink -f "$SCRIPTS_DIR/..")

# Application /tmp directory in flask-cam/tmp.
APP_TMP_DIR="$APP_DIR/tmp"

# Path to file containing previous IP address in flask-cam/tmp.
FILEPATH="$APP_TMP_DIR/ipaddress"

# Get current public/external IP address.
IP_ADDR=$(dig +short myip.opendns.com @resolver1.opendns.com)

# Create flask-cam/tmp if doesn't exist.
[[ -d "$APP_TMP_DIR" ]] || mkdir -p "$APP_TMP_DIR"

# Redirect current IP address to flask-cam/tmp/ipaddress if file doesn't exist
# or if file exists and current IP address different from previous.
# If IP changed (or on first run), run `sendmail.py` Python script to send
# email alert with new external IP address in the body.
if [ ! -f "$FILEPATH" ] || [ "$IP_ADDR" != "$(cat "$FILEPATH")" ]; then
  echo "IP changed"
  echo $IP_ADDR > "$FILEPATH"
  cd "$APP_DIR"
  python sendmail.py --subject "IP change" --body "$IP_ADDR"
fi
