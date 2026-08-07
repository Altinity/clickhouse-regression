# CAS server Jepsen (one runner)

Runs ClickHouse **server Set** Jepsen against a **CAS** disk (`metadata_type = cas`, PR #2159 naming)
backed by RustFS.
Topology matches the local Docker SSH harness: control host runs `lein`; nodes are privileged
Ubuntu containers with root SSH; RustFS is on the same Docker network (`jepsen-rustfs`).

## Layout

| Path | Role |
|------|------|
| `docker-compose.yml` | `jepsen-n1..n3`, `jepsen-keeper`, `jepsen-rustfs` |
| `jepsen.clickhouse/` | Vendored Clojure suite with CAS patches |
| `run.py` | CI/local entrypoint |
| `scripts/bringup.sh` | Keys, compose up, `nodes.txt` / `keeper.txt`, RustFS bucket |
| `scripts/teardown.sh` | Compose down |
| `scripts/resolve_binary.py` | `docker://` / `https://` / local path → binary |

## Requirements

- Docker Compose (privileged containers)
- JDK + [Leiningen](https://leiningen.org/) on the control host
- A CAS-capable ClickHouse binary (`package`)

## Local run

```bash
cd /path/to/clickhouse-regression
python3 cas/jepsen/run.py \
  --package /path/to/clickhouse \
  --minutes 5 \
  --test-count 8
```

`--minutes` is the **per-scenario** Jepsen `--time-limit` (converted to seconds).
With `--test-count 8`, wall time is roughly `8 × minutes` plus setup/teardown.

`--test-count` is how many of the server scenarios below to run (shuffled). Use `8` for the full matrix.

## Server scenarios (workload × nemesis)

There is a single server **workload**: `set` — clients insert unique numbers into a
`ReplicatedMergeTree` table on the CAS storage policy; after faults heal, Jepsen does one
final `SELECT` and checks that confirmed inserts were not lost and no unexpected values appear.

`test-all` pairs that workload with each of these **8 nemeses** (fault injectors):

| Nemesis | What it does |
|---------|----------------|
| `random-node-killer` | Sleep 5s, kill ClickHouse on a random node, sleep 5s, start it again. |
| `all-nodes-killer` | Kill ClickHouse on all nodes at once, sleep, then restart them. |
| `random-node-hammer-time` | `SIGSTOP` a random ClickHouse process (freeze), sleep 5s, then `SIGCONT`. |
| `all-nodes-hammer-time` | `SIGSTOP` all ClickHouse processes, sleep, then `SIGCONT`. |
| `simple-partitioner` | Split the cluster into two random halves with iptables (no traffic between halves). |
| `bridge-partitioner` | Two nodes cannot see each other, but both can see a third “bridge” node (and it can see both). |
| `blind-node-partitioner` | One victim cannot send to the others, but the others can still send to the victim (asymmetric). |
| `blind-others-partitioner` | The reverse asymmetry: others cannot send to the victim, but the victim can still send to them. |

After the timed load phase, Jepsen stops the nemesis (heal), waits briefly for recovery, then runs the final set read.

Short smoke:

```bash
python3 cas/jepsen/run.py --package /path/to/clickhouse --minutes 0.5 --test-count 1
```

## CI

Workflow: [`.github/workflows/run-cas-jepsen.yml`](../../.github/workflows/run-cas-jepsen.yml)

Dispatch with at least:

- `package` — `docker://…` or `https://…` (same as other regression workflows)
- `minutes` — per-scenario duration

## Pass / fail

- All scenarios `:valid? true` **and** `passed == --test-count` **and** Lein exit 0 → success
- Any `:valid? false` or `:valid? :unknown`, fewer results than expected, or non-zero Lein → failure
- Validity is from the **set** checker only (not `checker/perf` / gnuplot plots)
- Artifacts: `cas/jepsen/jepsen_run.log`, `cas/jepsen/jepsen.clickhouse/store/`
- `store/` is wiped at the start of each `run.py` invocation so stale results cannot mask failures

## Notes

- Disk config uses `metadata_type = cas` and storage policy `cas` (see `jepsen.clickhouse/resources/content_addressed_storage.xml`). Older trees that registered `content_addressed` need a matching binary/config.
- CAS endpoint DNS name `jepsen-rustfs` is fixed in that XML.
- `resolve_binary.py` fails fast on host/binary arch mismatch (e.g. arm64 deb on x86).
- Docker IPv4 listen patches are included in the vendored configs (`listen_host=0.0.0.0`).
- Do **not** pass Jepsen `--strict-host-key-checking` with 0.3.x: it is a boolean flag (presence turns checking **on**). Default is off; `bringup.sh` also refreshes `~/.ssh/known_hosts` via `ssh-keyscan`.
- Concurrent runs must use distinct `COMPOSE_PROJECT_NAME` (CI sets `jepsen-${{ github.run_id }}-${{ github.run_attempt }}`; local `bringup.sh` defaults to `jepsen-local-<pid>` and records it in `.compose_project` for teardown).
- `run.py` clears `jepsen.clickhouse/store/` before each run and requires `passed == --test-count` with Lein exit 0.
- Inserts use `insert_quorum = 2` and `async_insert = 0`; the final read does `SYSTEM SYNC REPLICA` after a post-heal sleep.
- CI installs `gnuplot` so optional Jepsen perf plots can be re-enabled without another runner gap.
