#!/bin/bash

LXDE_AUTOSTART=~/.config/lxsession/LXDE-pi/autostart
CHROMIUM_PREFS="~/.config/chromium/Default/Preferences"

# Use --incognito to prevent warnings being displayed on restart following
# poweroff without shutdown. Use --test-type to prevent "unsupported flag"
# flag message displayed when --ignore-certificate-errors is used, which is a
# valid flag but on the "bad flags" list of flags that reduce browser security.
CHROMIUM_FLAGS="--noerrdialogs --ignore-certificate-errors --test-type --kiosk --incognito"

URL="$1"
if [[ -z $URL ]]; then
  echo "Error: no URL provided"
  exit 1
fi

sudo apt install -y chromium-browser rng-tools unclutter

# `xset` commands disable screensaver power management. `unclutter` disables
# mouse pointer display. Modify chromium preferences to disable error message
# display.

if [[ -f $LXDE_AUTOSTART ]]; then
  mv $LXDE_AUTOSTART $LXDE_AUTOSTART.bak.$(date +"%Y%m%d%H%M%S")
fi

echo "@lxpanel --profile LXDE-pi
@pcmanfm --desktop --profile LXDE-pi

@xset s off
@xset -dpms
@xset s noblank
@unclutter -idle 0
@sed -i 's/"'"'"exited_cleanly"'"'": false/"'"'"exited_cleanly"'"'": true/' $CHROMIUM_PREFS
@chromium-browser $CHROMIUM_FLAGS $URL" > $LXDE_AUTOSTART
