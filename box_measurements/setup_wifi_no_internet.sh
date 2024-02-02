#!/bin/bash

name="Linux-WiFi-No-I"
passwd="password1"
# wifiif="wlp2s0"
wifiif="wlx00c0caada655"

echo "Setting up hotspot with name '$name' and password '$passwd'"
echo "Destroy AP by running Ctrl-C"

# Using the create_ap script from: https://github.com/oblique/create_ap.git

# -n: None - no internet sharing
sudo create_ap -n --freq-band 2.4 $wifiif $name $passwd

# RUnning as long as the user doesn't break the AP

echo "Closed AP"