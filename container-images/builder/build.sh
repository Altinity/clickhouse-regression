#!/usr/bin/env bash
set -e

#ccache -s # uncomment to display CCache statistics
mkdir -p /server/build_docker
cd /server/build_docker
cmake -G Ninja /server "-DCMAKE_C_COMPILER=$(command -v clang-11)" "-DCMAKE_CXX_COMPILER=$(command -v clang++-11)"

# Set the number of build jobs to CPUs rounded up -2

NUM_JOBS=$(( ($(nproc || grep -c ^processor /proc/cpuinfo) - 2) ))

ninja -j $NUM_JOBS && env TEST_OPT="--skip long compile $TEST_OPT" -j $NUM_JOBS
