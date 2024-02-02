#!/bin/bash

output_dir="$HOME/Documents/Code/Masterarbeit/nearbySharePcap"
pcap_path="/storage/self/primary/Download/PCAPdroid/"

# Using the adb service to get captured pcap files from the device


files=$(adb shell ls "$pcap_path")
echo $files
files=($files)

for pcap in "${files[@]}"
do
    echo "Pulling ${pcap} a"
    adb pull "${pcap_path}${pcap}" "$output_dir/$pcap"
done