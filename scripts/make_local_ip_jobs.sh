#!/bin/bash

# Where this script lives (flask-cam/scripts).
SCRIPTS_DIR=$(readlink -f $(dirname "$0"))

# Application temp directory (flask-cam/tmp).
APP_TMP_DIR=$(readlink -f "$SCRIPTS_DIR/../tmp")

UNINSTALL=false

while (( $# > 0 )); do
  case "$1" in
    uninstall)
      UNINSTALL=true
      shift 1
      ;;
  esac
done

if $UNINSTALL; then
  [[ ! -f /etc/network/if-up.d/get_local_ip ]] || sudo rm /etc/network/if-up.d/get_local_ip
  [[ ! -f /etc/cron.d/get_local_ip ]] || sudo rm /etc/cron.d/get_local_ip
  exit 0
fi

# Create flask-cam/tmp if it doesn't exist.
[[ -d "$APP_TMP_DIR" ]] || mkdir -p "$APP_TMP_DIR"

# Make script in /etc/network/if-up.d to be run on network service up.
# Sleep 40s because it can take some time after the network is up for
# wireless interface to actually connect and receive an IP address.
echo -e "#!/bin/bash
sleep 40s
$SCRIPTS_DIR/get_local_ip.sh -f $APP_TMP_DIR/local_network && chown $USER:$USER $APP_TMP_DIR/local_network" | \
  sudo tee /etc/network/if-up.d/get_local_ip > /dev/null \
  && sudo chmod +x /etc/network/if-up.d/get_local_ip

# Add cron job to run same script as above every 10 minutes.
echo -e "*/10 * * * * $USER $SCRIPTS_DIR/get_local_ip.sh -f $APP_TMP_DIR/local_network 2>&1" | \
  sudo tee /etc/cron.d/get_local_ip > /dev/null
