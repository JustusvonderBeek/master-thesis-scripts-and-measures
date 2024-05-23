#!/bin/bash

echo "Starting the quicheperf server..."

# Configuration
quicheperf_dir="/home/justus/Documents/Code/quicheperf-stun/target/debug/"
output_dir="./measurements/RealLifeQuicheperf"
# Read in configuration
config_dir="./"
config_file="real_intf_measure_conf.json"

mkdir -p "$output_dir"

server_conf=$(jq '.server' ${config_dir}$config_file)
listen_addr=$(echo $server_conf | jq -r '.listen_addr')
certificate=$(echo $server_conf | jq -r '.certificate')
key=$(echo $server_conf | jq -r '.key')
flags=$(echo $server_conf | jq -r '.flags')
stun=$(echo $server_conf | jq -r '.stun_url')
log_level=$(echo $server_conf | jq -r '.log_level')
interfaces=$(echo $server_conf | jq -r '.interfaces[]')

cmd="${quicheperf_dir}quicheperf server --cert ${certificate} --key ${key} -l ${listen_addr} ${flags} --stun-urls ${stun}"

date=$(date +"%d_%m")
time=$(date +"%H_%M")
test_dir="$output_dir/$date/$time"

echo "Creating test folder '$test_dir' and starting pcap capture..."
mkdir -p "$test_dir"
iface_string=""
for iface in $interfaces
do
    iface_string="${iface_string} -i $iface"
done
# Starting pcap capture (tshark so we can pre-filter interfaces)
tshark_cmd="tshark $iface_string -w ${test_dir}/server.pcap"

echo "Executing $cmd"

$(trap 'kill 0' SIGINT; export RUST_LOG="${log_level}"; $tshark_cmd & $cmd 2> "${test_dir}/server.log")

echo "Quicheperf server done"
echo "Wrote logfiles and pcaps to '$test_dir'"