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
    ./pull_pcap.sh $insideBox $in_filename $localPcapFilePath
    ./pull_pcap.sh $outsideBox $out_filename $localPcapFilePath

    # replace_names

    # Output the current list of all interfaces
    adb -s $insideBox shell ip a > "$localPcapFilePath/${insideBoxHumanRead}_ips.txt"
    adb -s $outsideBox shell ip a > "$localPcapFilePath/${outsideBoxHumanRead}_ips.txt"

    ./filter_pcap.sh "${localPcapFilePath}/$in_filename"
    ./filter_pcap.sh "${localPcapFilePath}/$out_filename"

    echo "Android nearby share test ended"
}

echo "Starting android nearby share test..."

insideBox="801KPRW1393526"
insideBoxHumanRead="mt_account"
outsideBox="801KPGS1389743"
outsideBoxHumanRead="my_account"

pcapFilePath="/sdcard/Download/"

dateNow="$(date +'%d_%m')"
timeNow="$(date +'%H_%M')"
if [[ $# -lt 2 ]]; then
    localPcapFilePath="measurements/whatsappPcap/${dateNow}/${timeNow}"
else
    localPcapFilePath="$2"
fi

# Create the current test directory
mkdir -p "$localPcapFilePath"

if [[ $# -lt 1 ]]; then
    in_filename="$insideBoxHumanRead.pcap"
    out_filename="$outsideBoxHumanRead.pcap"
else
    in_filename="in_$1"
    out_filename="out_${1}"
fi

inPcapFile="${pcapFilePath}${in_filename}"
outPcapFile="${pcapFilePath}${out_filename}"

echo "Saving to '$localPcapFilePath'"

# echo "Stop capture with CTRL+C"

# inShellCommand="su -c tcpdump -i any -w $inPcapFile"
# outShellCommand="su -c tcpdump -i any -w $outPcapFile"

# adb -s $insideBox shell "$inShellCommand" &
# inproc=$!
# adb -s $outsideBox shell "$outShellCommand" &
# outproc=$!

# # idle waiting for abort from user
# ( trap exit SIGINT; read -r -d '' _ </dev/tty )

# # (trap 'test_kill' SIGINT; adb -s $insideBox shell "$inShellCommand" & adb -s $outsideBox shell "$outShellCommand")&
# # (trap 'test_kill' SIGINT; adb -s $insideBox shell "$inShellCommand")&

# kill $inproc
# kill $outproc

# echo "Waiting for pcap capture to finish..."
# sleep 5

test_kill

# (trap 'test_kill' SIGINT; adb -s $outsideBox shell "$shellCommand")
