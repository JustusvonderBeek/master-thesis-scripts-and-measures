#!/bin/bash

echo "Starting the quicheperf client..."

# Configuration
quicheperf_dir="/home/justus/Documents/Code/quicheperf-stun/target/debug/"
output_dir="./measurements/RealLifeQuicheperf"
# Read in configuration
config_dir="./"
config_file="real_intf_measure_conf.json"

mkdir -p "$output_dir"

server_conf=$(jq '.server' ${config_dir}$config_file)
client_conf=$(jq '.client' ${config_dir}$config_file)
connect_addr=$(echo $server_conf | jq -r '.listen_addr')
listen_addr=$(echo $client_conf | jq -r '.listen_addr')
duration=$(echo $client_conf | jq -r '.duration')
bandwidth=$(echo $client_conf | jq -r '.bandwidth')
flags=$(echo $client_conf | jq -r '.flags')
stun=$(echo $client_conf | jq -r '.stun_url')
log_level=$(echo $client_conf | jq -r '.log_level')
interfaces=$(echo $client_conf | jq -r '.interfaces[]')

cmd="${quicheperf_dir}quicheperf client -l ${listen_addr} -c ${connect_addr} ${flags} -d ${duration} -b ${bandwidth} --stun-urls ${stun}"

date=$(date +"%d_%m")
time=$(date +"%H_%M")
test_dir="$output_dir/$date/$time"

echo "Creating test folder '$test_dir' and starting pcap capture..."
mkdir -p "$test_dir"
# Starting pcap capture (tshark so we can pre-filter interfaces)
iface_string=""
for iface in $interfaces
do
    iface_string="${iface_string} -i $iface"
done
# Starting pcap capture (tshark so we can pre-filter interfaces)
tshark_cmd="tshark $iface_string -w ${test_dir}/client.pcap"

echo "Executing: $cmd"
$(trap 'kill 0' SIGINT; export RUST_LOG="${log_level}"; $tshark_cmd & $cmd > "${test_dir}/client_perf.log" 2> "${test_dir}/client.log")

echo "Quicheperf server done"
echo "Wrote logfiles and pcaps to '$test_dir'"
