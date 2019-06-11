#!/bin/bash

usage() {
  SELF="${0##*/}"
  echo -e "USAGE
  $SELF [--addr] [--mask] [--help]

  Return the local (internal) IP address followed by the subnet mask.

  -a, --addr\t\treturn only the local IP address
  -m, --mask\t\treturn only the subnet mask
  -h, --help\t\tprint this message and exit"

  exit 1
}

# Determine whether to print only IP, only subnet mask, or both based on
# argument (or lack thereof).
PRINT_IP=true
PRINT_MASK=true

if (( $# > 0 )); then
  case "$1" in
    -a|--addr)
      PRINT_MASK=false
      ;;
    -m|--mask)
      PRINT_IP=false
      ;;
    -h|--help|*)
      usage
      ;;
  esac
fi

# Addresses in the private IP space begin with one of three blocks:
# 10.X.X.X
# 172.16.X.X - 172.31.X.X
# 192.168.X.X
# This grep regex parses the output of ifconfig to programmatically obtain
# the local IP address and subnet mask, taking into account different versions
# of ifconfig, some of which output `inet 192.168.X.X` and others
# `inet addr:192.168.X.X`.

IP_REGEX='inet [a-zA-Z\:]*(192\.168|10\.[0-9]+|172\.1[6789]|172\.2[0-9]|172\.3[01])\.[0-9]+\.[0-9]+'
MASK_REGEX='mask[ \:]*[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+'
MATCHING_LINE=$(ifconfig | egrep "$IP_REGEX")

if $PRINT_IP; then
  IP_ADDR=$(egrep -o "$IP_REGEX" <<< "$MATCHING_LINE" | egrep -o '[0-9]+.*[0-9]+')
  echo $IP_ADDR
fi

if $PRINT_MASK; then
  MASK=$(egrep -o "$MASK_REGEX" <<< "$MATCHING_LINE" | egrep -o '[0-9]+.*[0-9]+')
  echo $MASK
fi

exit 0
