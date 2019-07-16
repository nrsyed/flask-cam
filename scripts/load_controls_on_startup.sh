#!/bin/bash

RC_LOCAL_FILE=/etc/rc.local
CONTROLS_FILE=/usr/share/uvcdynctrl/data/046d/logitech.xml
COMMAND='$i uvcdynctrl -i '"$CONTROLS_FILE"
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
  sudo sed -i "/uvcdynctrl/d" "$RC_LOCAL_FILE"
  exit 0
fi

sudo sed -i -e "$COMMAND" "$RC_LOCAL_FILE"
