#!/bin/bash

# kill dnsmasq

# Find real Ethernet interface
eth_interface=$(ip -o link show | awk -F': ' '$2 !~ /lo|vir/{print $2; exit}')
echo "$eth_interface"
# Find real WiFi interface
# wifi_interface=$(ip -o link show | awk -F': ' '$2 !~ /lo|vir/{print $2; exit}' | tail -n 1)
# wifi_interface="wlx00c0caada655"
wifi_interface="wlp2s0"
echo "$wifi_interface"

wifi_ap="wlan0-ap"

# Set IP addresses for the interfaces
eth_ip="192.168.10.1"
wifi_ip="192.168.20.1"

# Set DHCP ranges
eth_dhcp_range="192.168.10.2,192.168.10.254,12h"
wifi_dhcp_range="192.168.20.2,192.168.20.254,12h"

# Set SSID and password for the access point
ssid="Linux-WiFi"
password="password1"

# Enable IP forwarding
echo 1 > /proc/sys/net/ipv4/ip_forward

# Configure iptables for packet forwarding
iptables -F
iptables -t nat -A POSTROUTING -o $eth_interface -j MASQUERADE
iptables -A FORWARD -i $eth_interface -o $wifi_interface -j ACCEPT
iptables -A FORWARD -i $wifi_interface -o $eth_interface -j ACCEPT


# Set IP addresses for interfaces
ip addr add $eth_ip/24 dev $eth_interface
# ip addr add $wifi_ip/24 dev $wifi_interface

# Start dnsmasq for DHCP on Ethernet interface
dnsmasq --conf-file=/dev/null --interface=$eth_interface --except-interface=lo --bind-interfaces --dhcp-range=$eth_dhcp_range --dhcp-option=option:dns-server,8.8.8.8

exit

# Configure the WiFi interface as an access point
iw dev $wifi_interface interface add $wifi_ap type __ap
ip link set dev $wifi_ap up
ip addr add $wifi_ip/24 broadcast 192.168.20.255 dev $wifi_ap

# Start hostapd with the specified configuration
cat <<EOL > /etc/hostapd/hostapd_bridge.conf
interface=$wifi_ap
ssid=$ssid
wpa_passphrase=$password
hw_mode=g
channel=6
wpa=2
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
EOL

hostapd /etc/hostapd/hostapd_bridge.conf &


# To remove: iw wlan0-ap del

# Start dnsmasq for DHCP on the WiFi interface
# dnsmasq --interface=$wifi_interface --dhcp-range=192.168.10.2,192.168.10.254,12h

# Start dnsmasq for DHCP on WiFi interface
dnsmasq --conf-file=/dev/null --interface=$wifi_interface --except-interface=lo --bind-interfaces --dhcp-range=$wifi_dhcp_range --dhcp-option=option:dns-server,8.8.8.8

echo "Bridge script executed successfully."
