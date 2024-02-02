#!/bin/bash

# Use: test_android <pcap_filename> <output_path>

replace_names() {
    echo "Replacing names with human readable format"
    for file in $localPcapFilePath*; do
        filename="${file##*/}"
        # echo "$file"
        replaced=${file//$insideBox/$insideBoxHumanRead}
        replaced=${replaced//$outsideBox/$outsideBoxHumanRead}
        # path=${file%/*}
        movedFile=$replaced
        if [[ "$file" != "$movedFile" ]]; then
            mv "$file" "$movedFile"
        fi
    done
}

test_kill() {
    # Pulling pcap files with pull script
    ./pull_pcap.sh $insideBox $filename $localPcapFilePath
    # ./pull_pcap.sh $outsideBox $filename $localPcapFilePath

    replace_names

    echo "Android nearby share test ended"
}

echo "Starting android nearby share test..."

insideBox="801KPRW1393526"
insideBoxHumanRead="box_pxl"
outsideBox="801KPGS1389743"
outsideBoxHumanRead="out_pxl"

pcapFilePath="/sdcard/Download/"

if [[ $# -lt 2 ]]; then
    localPcapFilePath="nearbySharePcap/"
else
    localPcapFilePath="$2"
fi
timeNow="$(date +"%d_%m_%H_%M")"
if [[ $# -lt 1 ]]; then
    filename=$timeNow
else
    filename="$1"
fi
filename="$filename.pcap"
pcapFile="${pcapFilePath}${filename}"

echo "Saving to $filename"

echo "Stop capture with CTRL+C"

shellCommand="su -c tcpdump -i any -w $pcapFile"

# (trap 'test_kill' SIGINT; adb -s $insideBox "$shellCommand" & adb -s $outsideBox "$shellCommand")
(trap 'test_kill' SIGINT; adb -s $insideBox shell "$shellCommand")
