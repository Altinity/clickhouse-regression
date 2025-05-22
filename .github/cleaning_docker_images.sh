#!/bin/bash

set -euo pipefail

echo "Scanning Docker images..."

# Get all images with digest, repository, tag, and creation time
docker images --digests --format '{{.Repository}} {{.Tag}} {{.Digest}} {{.ID}} {{.CreatedAt}}' | sort > /tmp/docker_images_list.txt

declare -A seen

while read -r line; do
    repo=$(awk '{print $1}' <<< "$line")
    tag=$(awk '{print $2}' <<< "$line")
    digest=$(awk '{print $3}' <<< "$line")
    image_id=$(awk '{print $4}' <<< "$line")
    created_at=$(awk '{print $5,$6,$7,$8,$9}' <<< "$line") # This is needed for full timestamp

    key="${repo}:${tag}"

    if [[ "$repo" != "<none>" && "$tag" == "<none>" ]]; then
        echo "Removing image with no tag/digest: $image_id"
        docker rmi -f "$image_id"
        continue
    fi
    
done < /tmp/docker_images_list.txt

echo "Cleanup complete."