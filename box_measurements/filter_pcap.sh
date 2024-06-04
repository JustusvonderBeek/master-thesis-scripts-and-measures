#!/bin/bash

# Usage: scrip.sh <infile> <outfile>

# In some cases, the pulled .pcap file contains many malformed packets
# This filter clears them

infile=$1
outfile=$1

if [ $# -gt 1 ]; then
    outfile=$2
fi

working_dir=$(dirname "$infile")

echo "Filtering '$infile' to '$outfile'"

# -r <input> -w <output> <filter>
tshark -r "$infile" -w "${working_dir}/tmp.pcap" !_ws.malformed

# Because tshark directly overwrites the file in case source and destination are the same
mv "${working_dir}/tmp.pcap" "$outfile"