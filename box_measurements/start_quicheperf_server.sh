#!/bin/bash

echo "Starting the quicheperf server..."

# Configuration
quicheperf_dir="/home/justus/Documents/Code/quicheperf-stun/target/debug/"
# Read in configuration
config_dir="./"
config_file="real_intf_measure_conf.json"

server_conf=$(jq '.server' ${config_dir}$config_file)
listen_addr=$(echo $server_conf | jq -r '.listen_addr')
certificate=$(echo $server_conf | jq -r '.certificate')
key=$(echo $server_conf | jq -r '.key')
flags=$(echo $server_conf | jq -r '.flags')

cmd="${quicheperf_dir}quicheperf server --cert ${certificate} --key ${key} -l ${listen_addr} ${flags}"

$cmd

echo "Quicheperf server done"