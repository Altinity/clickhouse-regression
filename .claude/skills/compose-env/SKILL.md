---
name: compose-env
description: Bring up a clickhouse-regression docker-compose cluster from a suite env folder without running regression.py, then open an interactive clickhouse client. Use when the user wants to start or stop a local test cluster, docker compose up inside cas_env/iceberg_env/s3_env or any *_env folder, or run manual SQL against those nodes.
---

# Compose env (no tests)

Bring up the same docker-compose cluster a suite uses, without running `regression.py`, then enter `clickhouse client` on a node.

Do **not** `cd` into an env folder and run raw `docker-compose up`. That skips image build, `CLICKHOUSE_TESTS_*` vars, and starting `clickhouse-server` (compose entrypoint is `tail -f /dev/null`). Use the script.

## Script

From `clickhouse-regression`:

```bash
python3 .claude/skills/compose-env/scripts/compose_env.py <command> --dir <ENV> [options]
```

Use the same Python env as tests (`pip3 install -r requirements.txt` / project venv). Needs `docker-compose` >= 2.23.1.

`--dir` is a suite name (`cas`), env folder (`cas/cas_env`), or omitted when cwd is the suite or env directory. On aarch64 the script selects `*_env_arm64` automatically.

## Workflow

```bash
python3 .claude/skills/compose-env/scripts/compose_env.py up --dir cas \
  --clickhouse docker://altinity/clickhouse-server:25.8.16.10002.altinitystable

python3 .claude/skills/compose-env/scripts/compose_env.py client --dir cas
python3 .claude/skills/compose-env/scripts/compose_env.py client --dir cas -s clickhouse2

python3 .claude/skills/compose-env/scripts/compose_env.py down --dir cas
```

From the env folder, omit `--dir`:

```bash
cd cas/cas_env
python3 ../../.claude/skills/compose-env/scripts/compose_env.py up \
  --clickhouse docker://altinity/clickhouse-server:25.8.16.10002.altinitystable
python3 ../../.claude/skills/compose-env/scripts/compose_env.py client
```

`client` is interactive (`docker-compose exec … clickhouse client`). Most env files `expose` 8123/9000 and do **not** publish them to the host — do not use `localhost`.

`list` prints `*_env` / `*_env_arm64` folders.

## `up`

`--clickhouse` is the same flag as `regression.py`:

- `docker://altinity/clickhouse-server:25.8.16.10002.altinitystable`
- `docker://clickhouse/clickhouse-server:head`
- local binary / `.deb` / `.tgz` / `https://...`

Also accepts `CLICKHOUSE_TESTS_SERVER_BIN_PATH`, or `/usr/bin/clickhouse` if present.

The package architecture must match the host. On x86_64 use `build_amd_release` / `*_amd64.deb`, not `*_arm64.deb`.

Optional flags (same meaning as tests): `--use-keeper`, `--base-os`, `--as-binary`, `--keeper`, `--zookeeper-version`, `--reuse-env`, `--set KEY=VALUE`, `--file other-compose.yml`.

MinIO defaults: `MINIO_ROOT_USER=admin`, `MINIO_ROOT_PASSWORD=password`.

`up` uses `helpers.cluster.Cluster` (TestFlows step output is expected). It does **not** tear down on exit. Data/logs: `<suite>/_instances/` (container-owned).

## Layout reminder

| Path | Role |
| --- | --- |
| `<suite>/<suite>_env/` | Compose project (`docker-compose.yml`) |
| `<suite>/<suite>_env_arm64/` | Same on aarch64 |
| `<suite>/configs/` | Bind-mounted ClickHouse config |
| `<suite>/_instances/<node>/logs/` | Server logs after `up` |
| `docker-compose/clickhouse-service.yml` | Shared ClickHouse service (`pull_policy: never`, dummy entrypoint) |

`CLICKHOUSE_TESTS_DIR` is the suite directory (parent that owns `configs/` / `regression.py`), not the env folder.

## Agent workflow

1. If the user names a suite or env folder, use it. Otherwise `list`, or cwd if it is already an env/suite dir.
2. Require `--clickhouse` unless a default path exists. Ask rather than guessing a version.
3. Run `up`. Then tell the user to run `client` themselves (interactive TTY). Do not start `regression.py` just to get a cluster.
4. Run `down` when the user is done, or if they want a clean recreate (skip `--reuse-env`).
5. To debug ClickHouse after `up`, read `_instances/<node>/logs/clickhouse-server.err.log` (see the testflows skill).
