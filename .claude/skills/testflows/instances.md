# `_instances` folder (ClickHouse, not TestFlows)

`_instances` is **not** produced by TestFlows. It is the host bind-mount of each Docker node's data and server logs, created when a suite cluster starts.

Gitignored (`_instances/` in `.gitignore`). Present only after a local (or CI) cluster run.

`CLICKHOUSE_TESTS_DIR` is the suite directory. Compose mounts:

```text
${CLICKHOUSE_TESTS_DIR}/_instances/<node>/logs/      →  /var/log/clickhouse-server/
${CLICKHOUSE_TESTS_DIR}/_instances/<node>/database/  →  /var/lib/clickhouse/
```

---

## Where it lives

| Suite | Path |
| --- | --- |
| alter | `alter/_instances/` |
| cas | `cas/_instances/` |
| other suites | `<suite>/_instances/` |

CI uploads `*/_instances/*.log` next to `raw.log`. Locally, look in the suite you ran.

---

## Layout (alter)

From `alter/alter_env/docker-compose.yml` after a run:

```text
alter/_instances/
  clickhouse1/
    logs/
      clickhouse-server.log        # full trace (large)
      clickhouse-server.err.log    # ERROR/FATAL — start here
      stderr.log
      stdout.log
    database/                      # /var/lib/clickhouse
      cores/                       # crash dumps
      data/  store/  metadata/  disks/ ...
  clickhouse2/                     # same shape
  clickhouse3/
  clickhouse-different-versions/   # extra node used by version-skew tests
  mysql1/database/
  postgres1/database/
  share/                           # shared host dir mounted into nodes
```

---

## Layout (cas)

From `cas/cas_env/docker-compose.yml`:

```text
cas/_instances/
  clickhouse1/
    logs/
      clickhouse-server.log
      clickhouse-server.err.log
      stderr.log
      stdout.log
    database/
      cores/
      disks/cas_disk/
      data/  store/  metadata/ ...
  clickhouse2/
  clickhouse3/
```

No mysql/postgres/share on the default cas env. Soak (`cas/soak/`) may use different compose files and node names (`ch1` / `ch2`); still look for `*/logs/*err*.log` under that env's data dir.

---

## Which file to open

| File | When |
| --- | --- |
| `logs/clickhouse-server.err.log` | **First.** Query errors, `LOGICAL_ERROR`, stack traces |
| `logs/stderr.log` | Startup path, sanitizer, abort, "Logging errors to ..." |
| `logs/clickhouse-server.log` | Trace around a timestamp / query id (huge) |
| `logs/stdout.log` | Rarely useful |
| `database/cores/` | Non-empty ⇒ crash; pair with `.err.log` / `stderr.log` |
| rotated `clickhouse-server.err.log.N` | If the current `.err.log` was rotated |

`stderr.log` typically starts with:

```text
Logging trace to /var/log/clickhouse-server/clickhouse-server.log
Logging errors to /var/log/clickhouse-server/clickhouse-server.err.log
```

Those container paths are the files under `_instances/<node>/logs/`.

Configs (`configs/clickhouse/config.xml`) set:

```xml
<log>/var/log/clickhouse-server/clickhouse-server.log</log>
<errorlog>/var/log/clickhouse-server/clickhouse-server.err.log</errorlog>
```

Some `config.d/logs.xml` files mention `log.log` / `log.err.log`. On disk after alter/cas runs the names are `clickhouse-server.log` and `clickhouse-server.err.log`. Glob if unsure:

```bash
ls -la alter/_instances/*/logs/
ls -la cas/_instances/*/logs/
```

---

## How to find the error

Check **every** ClickHouse node. A replica or keeper-related fail may only appear on `clickhouse2` / `clickhouse3`.

```bash
# Errors / fatals on all alter nodes
rg -n '<Error>|<Fatal>|LOGICAL_ERROR|Sanitizer|Aborted|Signal' \
  alter/_instances/*/logs/clickhouse-server.err.log \
  alter/_instances/*/logs/stderr.log

# Same for cas
rg -n '<Error>|<Fatal>|LOGICAL_ERROR|Sanitizer|Aborted|Signal' \
  cas/_instances/*/logs/clickhouse-server.err.log \
  cas/_instances/*/logs/stderr.log

# Window around a TestFlows fail timestamp (example)
rg -n '2026.08.12 15:19' alter/_instances/clickhouse1/logs/clickhouse-server.err.log

# Query / table from the test step
rg -n 'ATTACH PARTITION|table_name_here' alter/_instances/*/logs/clickhouse-server.err.log

# Cores
ls alter/_instances/*/database/cores cas/_instances/*/database/cores
```

`.err.log` lines look like:

```text
2026.08.12 15:19:19.692803 [ 39 ] {query-id} <Error> executeQuery: Code: 48. DB::Exception: ...
```

Use `{query-id}` to jump into `clickhouse-server.log` if you need the surrounding trace.

Skip routine startup `<Warning>` noise (`Include not found`, hugepages, integrity check) unless the test is about startup.

---

## Correlate with the TestFlows log

1. Leaf test path + Fail time from `tfs show messages`
2. SQL / table / partition from the `When` / `Then` step
3. Same timestamp and identifiers in `_instances/clickhouseN/logs/clickhouse-server.err.log`
4. If no server error: likely a test assertion (wrong result, timeout, cluster helper) — stay in `test.log`
5. If server `Error` / `Fatal` / core: treat as a ClickHouse bug unless the test expected that exception

---

## Other log dirs

CI may also collect Docker service logs in `<suite>/_service_logs/` (or `envs/<provider>/_service_logs`). That is still not TestFlows; it is `docker compose logs` for sidecar services (MinIO, proxy, keeper).
