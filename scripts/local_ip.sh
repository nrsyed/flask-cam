#!/bin/bash

# Addresses in the private IP space begin with one of three blocks:
# 10.X.X.X
# 172.16.X.X - 172.31.X.X
# 192.168.X.X
# This grep regex parses the output of ifconfig to programmatically obtain
# the local IP address, and takes into account different versions of ifconfig,
# some of which output `inet 192.168.X.X` and others `inet addr:192.168.X.X`.

REGEX='inet [a-zA-Z\:]*(192\.168|10\.[0-9]+|172\.1[6789]|172\.2[0-9]|172\.3[01])\.[0-9]+\.[0-9]+'
LOCAL_IP_ADDR=$(ifconfig | egrep -o "$REGEX" | egrep -o '[0-9]+.*[0-9]+')
echo $LOCAL_IP_ADDR
