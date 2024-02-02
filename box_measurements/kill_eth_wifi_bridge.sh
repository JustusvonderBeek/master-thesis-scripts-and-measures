#!/bin/bash

eth="enp3s0f1"
wifiBoard="wlp2s0"
wifiAdapter="wlx00c0caada655"
bridgename="eth-wifi"

ip link set $eth nomaster
ip link set $wifiBoard nomaster
ip link set $wifiAdapter nomaster
ip link del $bridgename