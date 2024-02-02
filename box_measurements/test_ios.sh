#!/bin/bash

# Use: test_ios <pcap_filename> <output_path>

test_kill() {
    # Pulling pcap files with pull script
    ./pull_pcap.sh $insideBox $filename $localPcapFilePath
    ./pull_pcap.sh $outsideBox $filename $localPcapFilePath

    echo "Android nearby share test ended"
}

echo "Starting iOS device test..."

# Get with: idevice_id -l
iPhone="00008020-001E50A62684002E"
iPad="00008027-000E11421187002E"

if [[ $# -lt 2 ]]; then
    localPcapFilePath="airdropPcap/"
else
    localPcapFilePath="$2"
fi
timeNow="$(date +"%d_%m_%H_%M")"
if [[ $# -lt 1 ]]; then
    filename=$timeNow
else
    filename="$1_$timeNow"
fi
filename="$filename.pcap"

# Hardcoded for this test
(trap 'kill 0' SIGINT; $HOME/Documents/Code/rvi_capture/rvi_capture.py --udid $iPhone "${localPcapFilePath}iphone_$filename" & $HOME/Documents/Code/rvi_capture/rvi_capture.py --udid $iPad "${localPcapFilePath}ipad_$filename")

echo "iOS device test finished"