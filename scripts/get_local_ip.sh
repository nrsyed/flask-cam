#!/bin/bash

usage() {
  SELF="${0##*/}"
  echo -e "USAGE
  $SELF [--file <filepath>] [--help]

  Return the local (internal) IP address and subnet mask.

  -f, --file
      write the IP and subnet mask to a file (only if the string is not blank).

  -h, --help
      print this message and exit"

  exit 1
}

while (( $# > 0 )); do
  case "$1" in
    -f|--file)
      FILEPATH="$2"
      shift 2
      ;;
    -h|--help|*)
      usage
      ;;
  esac
done

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
MATCHING_LINE=$(/sbin/ifconfig | egrep "$IP_REGEX")

IP_ADDR=$(egrep -o "$IP_REGEX" <<< "$MATCHING_LINE" | egrep -o '[0-9]+.*[0-9]+')
MASK=$(egrep -o "$MASK_REGEX" <<< "$MATCHING_LINE" | egrep -o '[0-9]+.*[0-9]+')

RESULT="$IP_ADDR/$MASK"

if [[ -n "$FILEPATH" ]] && [[ -n "$RESULT" ]]; then
  echo "$RESULT" > "$FILEPATH"
else
  echo "$RESULT"
fi

exit 0
