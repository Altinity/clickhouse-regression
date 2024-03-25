#!/bin/bash

SCRIPT_DIR=$(dirname "$0")

# Check if the script is running as root
if [ "$(id -u)" -ne "0" ]; then
    echo "This script must be run as root."
    exit 1
fi

cd "$SCRIPT_DIR/../"

umount _instances/*/*