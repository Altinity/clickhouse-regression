#!/bin/bash
# Start ClickHouse, then a virtual display with a window manager and an
# accessibility bus, and wait. The tests start DBeaver with `docker exec`
# (see steps/environment.py) and run /desktop.py for every action.
# /tmp/desktop.env holds the environment those commands need; /tmp/ready is
# created when everything is up.
set -x

# The image's own entrypoint, so the server runs with the image's configuration.
/entrypoint.sh > /results/logs/clickhouse-server.log 2>&1 &
for i in $(seq 1 120); do
    clickhouse-client -q "SELECT 1" > /dev/null 2>&1 && break
    sleep 1
done
clickhouse-client -q "SELECT version()"

export DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x24 -nolisten tcp &
for i in $(seq 1 60); do
    xdpyinfo > /dev/null 2>&1 && break
    sleep 0.5
done
eval "$(dbus-launch --sh-syntax)"
cat > /tmp/desktop.env <<ENV
export DISPLAY=:99
export DBUS_SESSION_BUS_ADDRESS='$DBUS_SESSION_BUS_ADDRESS'
export GTK_MODULES=gail:atk-bridge
ENV
/usr/libexec/at-spi-bus-launcher --launch-immediately &
openbox &
touch /tmp/ready
sleep infinity
