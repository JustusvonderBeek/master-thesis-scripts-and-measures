#!/bin/bash

name="WiFi-In-Box"
passwd="password1"
wifiAdapter="wlx00c0caada655"
wifiOnboard="wlp2s0"

echo "Setting up hotspot with name '$name' and password '$passwd'"
echo "Destroy AP by running Ctrl-C"

# Using the create_ap script from: https://github.com/oblique/create_ap.git

sudo create_ap --freq-band 2.4 --no-virt $wifiAdapter $wifiOnboard $name $passwd

# RUnning as long as the user doesn't break the AP

echo "Closed AP"
