#!/bin/bash

# Where this script lives, i.e., the /scripts directory.
SCRIPTS_DIR=$(readlink -f $(dirname "$0"))

# Add a file to /etc/cron.d for a job that runs flask-cam/scripts/ipcheck.sh
# every 15 minutes as the current user and logs any output to syslog under the
# name 'IPCHECK'.
echo "*/15 * * * * $USER $SCRIPTS_DIR/external_ip_check.sh 2>&1 | /usr/bin/logger -t IPCHECK" | sudo tee /etc/cron.d/external_ip_check > /dev/null
