#!/bin/bash

# Use: pull_pcap <device> <filename> [output]

echo "Pulling PCAP file $2 from $1"

if [[ $# -le 2 ]]; then
    echo "Usage: pull_pcap <device> <filename>"
    exit 1
fi

pcapFolder="/sdcard/Download/"
device=$1
filename=$2
if [[ $# -lt 3 ]]; then
    outputPath="../nearbySharePcap/"
else
    outputPath=$3
fi

echo "Pulling pcap to $outputPath"

adb -s $device pull ${pcapFolder}${filename} "$outputPath/${filename}"

# Remove file after pulling successful
if [[ -f "$outputPath/${device}_${filename}" ]]; then
    echo "Deleting file after download"
    adb -s $device shell rm -r $pcapFolder/$filename
fi