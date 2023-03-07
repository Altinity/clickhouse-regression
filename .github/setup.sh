#!/bin/bash

sudo rm -rf /var/lib/apt/lists/* && set -x
sudo rm -rf /var/cache/debconf && set -x
sudo rm -rf /tmp/* && set -x
sudo apt-get clean && set -x
sudo pip install -r pip_requirements.txt && set -x
sudo apt-get update && set -x
mkdir example/_instances && set -x
env && set -x
uname -i && set -x
python3 -c "import platform; print('Platform machine:', platform.machine())" && set -x
