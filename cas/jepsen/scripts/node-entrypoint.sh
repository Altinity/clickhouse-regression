#!/usr/bin/env bash
# Bootstrap a privileged Ubuntu container as a Jepsen SSH node.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

apt-get update -qq
apt-get install -y -qq \
  openssh-server sudo iptables iproute2 curl wget ca-certificates \
  tar gzip psmisc procps >/dev/null

mkdir -p /run/sshd /root/.ssh /home/robot-clickhouse /var/log/clickhouse-keeper
if [[ -f /tmp/jepsen_authorized_keys ]]; then
  cp /tmp/jepsen_authorized_keys /root/.ssh/authorized_keys
fi
chmod 700 /root/.ssh
chmod 600 /root/.ssh/authorized_keys

sed -i 's/#*PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config
grep -q '^PasswordAuthentication' /etc/ssh/sshd_config \
  && sed -i 's/^PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config \
  || echo 'PasswordAuthentication no' >> /etc/ssh/sshd_config

ssh-keygen -A
exec /usr/sbin/sshd -D -e
