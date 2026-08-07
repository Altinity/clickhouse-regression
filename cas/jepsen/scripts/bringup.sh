#!/usr/bin/env bash
# Bring up Jepsen SSH nodes + RustFS and write nodes.txt / keeper.txt.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PROJECT="${COMPOSE_PROJECT_NAME:-jepsen-local-$$}"
export COMPOSE_PROJECT_NAME="$PROJECT"
echo "$PROJECT" > "$ROOT/.compose_project"
COMPOSE=(docker compose -p "$PROJECT" -f docker-compose.yml)
NETWORK="${PROJECT}_jepsen-net"

cid() {
  "${COMPOSE[@]}" ps -q "$1"
}

ip_of() {
  local id
  id="$(cid "$1")"
  if [[ -z "$id" ]]; then
    echo "ERROR: no container for service $1 in project $PROJECT" >&2
    exit 1
  fi
  docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "$id"
}

if [[ ! -f id_rsa ]]; then
  ssh-keygen -t rsa -b 2048 -N '' -f id_rsa >/dev/null
fi
chmod 600 id_rsa
chmod 644 id_rsa.pub

# Tear down this project only (concurrent runs use distinct COMPOSE_PROJECT_NAME).
"${COMPOSE[@]}" down -v --remove-orphans 2>/dev/null || true
"${COMPOSE[@]}" up -d --remove-orphans --force-recreate

SSH_OPTS=(-i id_rsa -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o GlobalKnownHostsFile=/dev/null -o ConnectTimeout=2 -o BatchMode=yes)

echo "Waiting for SSH on Jepsen nodes (project=$PROJECT)..."
for name in jepsen-n1 jepsen-n2 jepsen-n3 jepsen-keeper; do
  ok=0
  for _ in $(seq 1 90); do
    ip="$(ip_of "$name" 2>/dev/null || true)"
    if [[ -n "$ip" ]] && ssh "${SSH_OPTS[@]}" "root@$ip" 'true' 2>/dev/null; then
      ok=1
      break
    fi
    sleep 2
  done
  if [[ "$ok" -ne 1 ]]; then
    echo "ERROR: SSH not ready on $name" >&2
    id="$(cid "$name" 2>/dev/null || true)"
    if [[ -n "$id" ]]; then
      docker logs "$id" 2>&1 | tail -40 >&2 || true
    fi
    exit 1
  fi
  echo "  $name ready"
done

{
  ip_of jepsen-n1
  ip_of jepsen-n2
  ip_of jepsen-n3
} > nodes.txt
ip_of jepsen-keeper > keeper.txt

echo "Waiting for RustFS on network $NETWORK..."
rustfs_ok=0
for _ in $(seq 1 60); do
  if docker run --rm --network "$NETWORK" --entrypoint /bin/sh minio/mc:latest -c \
    'mc alias set local http://jepsen-rustfs:11121 clickhouse clickhouse >/dev/null 2>&1 && mc ls local >/dev/null 2>&1'; then
    rustfs_ok=1
    break
  fi
  sleep 2
done
if [[ "$rustfs_ok" -ne 1 ]]; then
  echo "ERROR: RustFS not reachable on $NETWORK" >&2
  id="$(cid jepsen-rustfs 2>/dev/null || true)"
  if [[ -n "$id" ]]; then
    docker logs "$id" 2>&1 | tail -80 >&2 || true
  fi
  exit 1
fi

echo "Creating CAS bucket..."
if ! docker run --rm --network "$NETWORK" --entrypoint /bin/sh minio/mc:latest -c '
mc alias set local http://jepsen-rustfs:11121 clickhouse clickhouse >/dev/null
mc mb -p local/test >/dev/null 2>&1 || true
mc rm -r --force local/test/jepsen_cas/ >/dev/null 2>&1 || true
mc ls local/test >/dev/null
'; then
  echo "ERROR: failed to prepare RustFS bucket test/jepsen_cas" >&2
  exit 1
fi

KEY="$ROOT/id_rsa"
SSH_CLEAN=(-i "$KEY" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o GlobalKnownHostsFile=/dev/null -o BatchMode=yes)
for ip in $(cat nodes.txt) $(cat keeper.txt); do
  ssh "${SSH_CLEAN[@]}" "root@$ip" \
    'killall -9 clickhouse 2>/dev/null || true; rm -rf /home/robot-clickhouse/{db,logs,config,clickhouse.pid}; mkdir -p /home/robot-clickhouse /var/log/clickhouse-keeper'
done

# Refresh OpenSSH known_hosts so Jepsen/sshj can verify ephemeral container host keys.
mkdir -p "$HOME/.ssh"
touch "$HOME/.ssh/known_hosts"
for ip in $(cat nodes.txt) $(cat keeper.txt); do
  ssh-keygen -R "$ip" >/dev/null 2>&1 || true
  ssh-keyscan -H "$ip" >> "$HOME/.ssh/known_hosts" 2>/dev/null || true
done

echo "COMPOSE_PROJECT_NAME=$PROJECT"
echo "nodes.txt:"
cat nodes.txt
echo "keeper.txt:"
cat keeper.txt
echo "Bringup complete."
