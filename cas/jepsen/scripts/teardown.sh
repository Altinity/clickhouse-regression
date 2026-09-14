#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PROJECT="${COMPOSE_PROJECT_NAME:-}"
if [[ -z "$PROJECT" && -f "$ROOT/.compose_project" ]]; then
  PROJECT="$(cat "$ROOT/.compose_project")"
fi
if [[ -z "$PROJECT" ]]; then
  echo "COMPOSE_PROJECT_NAME unset and no .compose_project; nothing to tear down."
  exit 0
fi

docker compose -p "$PROJECT" -f docker-compose.yml down -v --remove-orphans 2>/dev/null || true
rm -f "$ROOT/.compose_project"
echo "Teardown complete for project $PROJECT."
