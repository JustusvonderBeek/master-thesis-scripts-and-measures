#!/bin/bash

# Usage: <script.sh> from to

echo "Pulling remote testing files"

# Parsing the given config file with jq
config_file="pull_config.json"
if [ $# -lt 2 ]; then
    echo "Either 'from' or 'to' is missing!"
    exit 1
fi

from="$1"
to="$2"

if [ "$from" == "$to" ]; then
    echo "Source and destination are equal, cannot perform this action!"
    exit 1
fi

# Parse the config per device
desktop=$(jq '.desktop' $config_file)
laptop=$(jq '.laptop' $config_file)
aws=$(jq '.aws' $config_file)
raspberry=$(jq '.raspberry' $config_file)

case "$from" in
    "desktop")
    from_conf="$desktop"
    ;;
    "laptop")
    from_conf="$laptop"
    ;;
    "raspberry")
    from_conf="$raspberry"
    ;;
    "aws")
    from_conf="$aws"
    ;;
    *)
    echo "Unknown from device '$from'..."
    exit 1
    ;;
esac

case "$to" in
    "desktop")
    to_conf="$desktop"
    ;;
    "laptop")
    to_conf="$laptop"
    ;;
    "raspberry")
    to_conf="$raspberry"
    ;;
    "aws")
    to_conf="$aws"
    ;;
    *)
    echo "Unknown from device '$from'..."
    exit 1
    ;;
esac

remote_ssh=$(echo $from_conf | jq -r '.ssh')
remote_path=$(echo $from_conf | jq -r '.working_dir')
local_path=$(echo $to_conf | jq -r '.working_dir')

echo "Starting to pull all files..."
# Copy all folders found in remote to local and keep times
echo "$remote_ssh"
echo "$remote_path"
echo "$local_path"

rsync -rt "$remote_ssh":"$remote_path/" "$local_path"

echo "Pulled all remote files"