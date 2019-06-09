#!/bin/bash

# Where this script lives, i.e., flask-cam/scripts
SCRIPTS_DIR=$(readlink -f $(dirname "$0"))

# Main application directory one level up from this one.
APP_DIR=$(readlink -f "$SCRIPTS_DIR/..")

# Where Python executable lives.
PYTHON_DIR=$(dirname "$(which python)")

THREADS=5
TIMEOUT=30

# Add a systemd unit file in /etc/systemd/system to start a gunicorn instance
# to run the app.
echo "[Unit]
Description=Gunicorn daemon for flaskcam
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=$APP_DIR
Environment=\"PATH=$PYTHON_DIR\"
ExecStart=$PYTHON_DIR/gunicorn --timeout $TIMEOUT --workers 1 --threads $THREADS --bind unix:flaskcam.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target" | sudo tee /etc/systemd/system/flaskcam.service > /dev/null
