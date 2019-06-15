#!/bin/bash

# Where this script lives, i.e., the /scripts directory.
SCRIPTS_DIR=$(readlink -f $(dirname "$0"))

# Path to cron job file.
CRON_JOB_PATH=/etc/cron.d/external_ip_check

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
  [[ ! -f "$CRON_JOB_PATH" ]] || sudo rm "$CRON_JOB_PATH"
fi

# Add a file to /etc/cron.d for a job that runs flask-cam/scripts/ipcheck.sh
# every 15 minutes as the current user and logs any output to syslog under the
# name 'IPCHECK'.
echo "*/15 * * * * $USER $SCRIPTS_DIR/external_ip_check.sh 2>&1 | /usr/bin/logger -t IPCHECK" | sudo tee "$CRON_JOB_PATH" > /dev/null
