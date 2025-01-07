#!/bin/bash
set -e
echo "Build image"
docker build -t registry.gitlab.com/altinity-qa/clickhouse/cicd/regression/benchmark/image .
