#!/bin/bash

echo "Bridging eth and wifi interface"

eth="enp3s0f1"
wifiBoard="wlp2s0"
wifiAdapter="wlx00c0caada655"
bridgename="eth-wifi"

ip link del $bridgename
ip link add name $bridgename type bridge
ip link set dev $bridgename up
ip link set dev $eth master $bridgename
ip link set dev $wifiBoard master $bridgename
ip link set dev $wifiAdapter master $bridgename

echo "Ethernet and WiFi (adapter) bridged"