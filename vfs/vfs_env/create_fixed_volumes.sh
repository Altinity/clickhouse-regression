#!/bin/bash

SCRIPT_DIR=$(dirname "$0")
INSTANCES_DIR="$SCRIPT_DIR/../_instances"

CLICKHOUSE_FOLDERS=("database" "logs")
VOLUME_SIZE="100M"

if [ "$(id -u)" -ne "0" ]; then
    echo "This script must be run as root."
    exit 1
fi

if [ ! -d "$INSTANCES_DIR" ]; then
    mkdir "$INSTANCES_DIR"
fi

cd "$INSTANCES_DIR"

for i in {1..3}; do
    for SUBFOLDER in "${CLICKHOUSE_FOLDERS[@]}"; do
        NEW_FOLDER="clickhouse$i/$SUBFOLDER"
        mkdir -p $NEW_FOLDER
        mount -o size="$VOLUME_SIZE" -t tmpfs none "$NEW_FOLDER"
    done
done



