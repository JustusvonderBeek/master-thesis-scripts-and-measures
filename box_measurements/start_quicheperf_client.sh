#!/bin/bash

echo "Starting the quicheperf client..."

# Configuration
quicheperf_dir="/home/justus/Documents/Code/quicheperf-stun/target/debug/"
# Read in configuration
config_dir="./"
config_file="real_intf_measure_conf.json"

server_conf=$(jq '.server' ${config_dir}$config_file)
client_conf=$(jq '.client' ${config_dir}$config_file)
connect_addr=$(echo $server_conf | jq -r '.listen_addr')
listen_addr=$(echo $client_conf | jq -r '.listen_addr')
duration=$(echo $client_conf | jq -r '.duration')
bandwidth=$(echo $client_conf | jq -r '.bandwidth')
flags=$(echo $client_conf | jq -r '.flags')
stun=$(echo $client_conf | jq -r '.stun-url')

cmd="${quicheperf_dir}quicheperf client -l ${listen_addr} -c ${connect_addr} ${flags} -d ${duration} -b ${bandwidth} --stun-url ${stun}"

echo "Would execute: $cmd"
$cmd

echo "Quicheperf server done"