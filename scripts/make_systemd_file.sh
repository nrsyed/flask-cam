#!/bin/bash

# Create systemd unit file to create the `flaskcam` service.

# Where this script lives, i.e., flask-cam/scripts
SCRIPTS_DIR=$(readlink -f $(dirname "$0"))

# Main application directory one level up from this one.
APP_DIR=$(readlink -f "$SCRIPTS_DIR/..")

# Where Python executable lives.
PYTHON_DIR=$(dirname "$(which python)")

THREADS=5
TIMEOUT=30
UNINSTALL=false

while (( $# > 0 )); do
  case "$1" in
    --threads)
      THREADS="$2"
      shift 2
      ;;
    --timeout)
      TIMEOUT="$2"
      shift 2
      ;;
    uninstall)
      UNINSTALL=true
      shift 1
      ;;
  esac
done

if $UNINSTALL; then
  sudo systemctl stop flaskcam
  sudo systemctl disable flaskcam
  sudo rm /etc/systemd/system/flaskcam.service
  exit 0
fi

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

# Start and enable the service.
sudo systemctl start flaskcam
sudo systemctl enable flaskcam
