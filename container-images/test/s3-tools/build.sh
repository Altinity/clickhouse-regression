#!/bin/bash
set -e
echo "Build image"
docker build -t registry.gitlab.com/altinity-public/container-images/s3-tools .
