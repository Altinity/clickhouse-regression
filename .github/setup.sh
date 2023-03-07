#!/bin/bash

set -x
sudo rm -rf /var/lib/apt/lists/*
sudo rm -rf /var/cache/debconf
sudo rm -rf /tmp/*
sudo apt-get clean
sudo pip install -r pip_requirements.txt
sudo apt-get update
mkdir example/_instances
env
uname -i
python3 -c "import platform; print('Platform machine:', platform.machine())"
