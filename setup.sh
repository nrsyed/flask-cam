#!/bin/bash

# Where this script lives (flask-cam/).
APP_DIR=$(readlink -f $(dirname "$0"))

SCRIPTS_DIR="$APP_DIR/scripts"

PORT=""
UNINSTALL=false
SKIP_OPENCV=false

while (( $# > 0 )); do
  case "$1" in
    -p|--port)
      PORT="$2"
      shift 2
      ;;
    --skip-opencv)
      SKIP_OPENCV=true
      shift 1
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
  cd "$SCRIPTS_DIR"
  ./make_external_ip_check_cronjob.sh uninstall
  ./make_nginx_config.sh uninstall
  ./make_local_ip_jobs.sh uninstall
  ./make_systemd_file.sh uninstall
  exit 0
fi

if [[ -z "$PORT" ]]; then
  echo "Error: port required (use --port)"
  exit 1
fi

sudo apt update && sudo apt upgrade
sudo apt -y install dnsutils libffi-dev nginx uvcdynctrl

cd "$APP_DIR"
pip install -r requirements.txt
$SKIP_OPENCV || pip install opencv-python

cd "$SCRIPTS_DIR"
./make_systemd_file.sh
./make_nginx_config.sh --port $PORT
./make_local_ip_jobs.sh
./make_external_ip_check_cronjob.sh

printf "Add authenticated user now? (y/n): "
read SELECTION
if [[ "$SELECTION" == "y" ]]; then
  cd "$APP_DIR"
  printf "Username: "
  read USERNAME
  printf "Password: "
  read -s PASSWORD
  echo
  python password.py --add-user --user "$USERNAME" --password "$PASSWORD" -f "$APP_DIR/users"
  if [[ ! $? == 0 ]] ; then
    echo "Error adding user"
  else
    echo "User $USERNAME added to $APP_DIR/users"
  fi
fi
