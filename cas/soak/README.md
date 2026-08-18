# CAS soak suite

Port of ClickHouse [`utils/ca-soak`](https://github.com/Altinity/ClickHouse/tree/cas-gc-rebuild/utils/ca-soak)
from [PR #2073](https://github.com/Altinity/ClickHouse/pull/2073) (`cas-gc-rebuild` @ `684161dcc03`)
into `clickhouse-regression` as a **separate** suite under `cas/soak`.

`cas/regression.py` does **not** include this suite. Metadata type is **`cas`**.

```bash
pip install -r cas/soak/requirements.txt   # pytest + optional deps

python3 cas/soak/regression.py --local \
  --clickhouse 'docker://altinity/clickhouse-server:<cas-tag>' \
  --suite unit,phase1 --seed 1
```

Or from this directory:

```bash
cd cas/soak && ./regression.py --local --clickhouse /path/to/clickhouse --as-binary --suite all
```

## Suites (`--suite`)

| Suite | What it runs | Cluster |
|-------|----------------|---------|
| `unit` | pytest under `tests/` + `scenarios/tests/` | none |
| `phase1` | Deterministic green-path soak (`soak.run --phase 1`) | `helpers.cluster` / `soak_env` |
| `phase2` | Same + chaos faults (`--phase 2`) | `helpers.cluster` / `soak_env` |
| `phase3` | Wall-clock staged soak (`--phase 3`, default `--phase3-duration 15m`) | `helpers.cluster` / `soak_env` |
| `scenarios` | Adversarial cards S01–S45 (`scenarios.run`) | own compose variants |
| `all` | `unit,phase1,phase2,phase3,scenarios` | mixed (`soak_env` is torn down before scenarios so host ports 8123/8124 are free) |

Binary / package is specified like every other regression suite:

- `--clickhouse` / `--clickhouse-binary-path` / `--clickhouse-package-path`
- `docker://…`, `https://…/*.deb`, local `.deb` / binary
- `--as-binary` when you want the bare-binary install path

## How soak works (short)

1. A single `--seed` drives a deterministic op ledger (`soak.ledger`).
2. Workers apply INSERT/OPTIMIZE concurrently; UPDATE/DELETE/TRUNCATE/DROP are barriers.
3. An in-memory integer-aggregate `Model` mirrors every op.
4. Quiesced checkpoints assert: both replicas == model, `cas-fsck` `dangling==0` and `stale_edge==0`, GC dry-run ⊆ unreachable.
5. Phase 2/3 add chaos (`docker kill/restart/pause`) and longer wall-clock stages.

Under `helpers.cluster`, `bridge.bind_cluster()` sets `CA_SOAK_NODE{i}_{HOST,PORT,CONTAINER}` so the
ported driver talks to published ports `8123`/`8124` and `docker exec`s the real container ids.

Scenario variants that need special topology still use the adapted `docker-compose-*.yml` files with
`${CLICKHOUSE_BINARY_HOST_PATH}` (filled from the same `--clickhouse` argument).

## CI workflow

GitHub Actions: [`.github/workflows/run-cas-soak.yml`](../../.github/workflows/run-cas-soak.yml)

Dispatch with `package` + `version` to run `--suite all` (long timeout).

## Soak driver phases

| Phase | Description |
|-------|-------------|
| 1 | Green-path smoke: seeded ledger, checkpoints, no chaos |
| 2 | Phase 1 + deterministic chaos schedule |
| 3 | Timed stages (warmup → steady → mutations → TTL → GC → chaos → cliff → converge); default full run is 24h |

## Scenario cards (S01–S45)

| ID | Description |
|----|-------------|
| `S01` | huge single blob |
| `S02` | huge duplicate blob |
| `S03` | million-live-object idle GC |
| `S04` | million-object orphan drain |
| `S05` | 10000 sparse tables |
| `S06` | 10000-column wide part |
| `S07` | manifest cap fail-closed |
| `S08` | thousands of parts created quickly |
| `S09` | mutation carry-forward |
| `S10` | patch parts and lightweight deletes |
| `S11` | heavy ALTER TABLE ... DELETE |
| `S12` | ten replicas, shared pool, parallel inserts |
| `S13` | process loss during write and GC |
| `S14` | restart with many refs |
| `S15` | GC target-shard comparison |
| `S16` | hot content cycle with GC |
| `S17` | detached, attach, and drop detached |
| `S18` | freeze and unfreeze shadows |
| `S19` | clone and partition movement |
| `S20` | replicated fetch and relink |
| `S21` | read-heavy many-ref workload |
| `S22` | object-store throttling and retry budget |
| `S23` | idle shared pool baseline |
| `S24` | small dedup-cache capacity |
| `S25` | non-Atomic database paths |
| `S26` | table-level verbatim file churn |
| `S27` | backend list pagination ambiguity |
| `S28` | concurrent wide/large insert scratch pressure |
| `S29` | large non-direct-blob file memory spike |
| `S30` | repeated create/drop namespace churn |
| `S31` | cas-gc-dryrun completeness under gc_shards>1 |
| `S32` | TTL expiry reclaim |
| `S33` | concurrent explicit GC leaders — reclaim-leak regression guard |
| `S34` | create/drop churn — D1 bounded GC fanout |
| `S35` | rapid same-name rotation — D1 incarnation monotonicity |
| `S36` | MOVE PART/PARTITION between local and CA disks (both directions) |
| `S37` | multi-disk storage policies (local+CA, local+local+CA) |
| `S38` | unclean handover: the epoch seal makes a late predecessor PUT lose |
| `S39` | mount-lease resilience under a degraded-but-alive S3 (fix #37) |
| `S40` | acked-then-lost INSERT under S3 outage + replica kill |
| `S41` | wide-insert write-path baseline (CA vs plain S3) |
| `S42` | allocation-fault soak (query-thread): exception safety of the CAS post-durable window |
| `S43` | same-uuid pool recreation refuses a residual survivor write |
| `S44` | rebirth adversarial with concurrent namespace-file (mutation) readers/writers |
| `S45` | decommission a victim member with hidden Removing catalog entries |

Filter with `--scenario S01` / `P0` / `all` (see `python3 -m scenarios.run --list`).

## Unit tests (`tests/`)

Harness unit tests live under `tests/` (ledger, model, fsck parsers, chaos retries, signals, …)
plus scenario framework tests under `scenarios/tests/`.

## Compose variants (scenario infra)

| File | Topology |
|------|----------|
| `docker-compose.yml` | Default 2×CH + RustFS + Keeper |
| `docker-compose-tuned.yml` | Tuned CA settings overlay |
| `docker-compose-gc_shards2.yml` | `gc_shards=2` |
| `docker-compose-gc_shards8.yml` | `gc_shards=8` (S15) |
| `docker-compose-10replicas.yml` | 10 replicas shared pool (S12) |
| `docker-compose-small_dedup_cache.yml` | Tiny dedup cache (S24) |
| `docker-compose-multidisk.yml` | local+CA policies (S36/S37) |
| `docker-compose-s3faultproxy.yml` | S3 fault proxy (S22/S39/…) |
| `docker-compose-s38.yml` | Late-PUT topology (S38) |
| `docker-compose-s41.yml` | Isolated 1-node write baseline (S41) |
| `docker-compose-awss3.yml` | Real AWS S3 |
| `docker-compose-gcs.yml` | GCS |

## Layout

```
cas/soak/
  regression.py          # TestFlows entrypoint (this suite)
  bridge.py              # helpers.cluster → CA_SOAK_* env
  features.py            # unit / phase1-3 / scenarios features
  soak_env/              # helpers.cluster compose (x86)
  soak_env_arm64/        # helpers.cluster compose (ARM)
  configs/               # soak + regression ClickHouse configs (metadata_type=cas)
  soak/                  # driver package (run, ledger, model, chaos, …)
  scenarios/             # S01–S45 cards + framework
  tests/                 # pytest unit tests
  docker-compose*.yml    # scenario topology variants
  scripts/ tools/ proxy/ # upstream helpers
```

Upstream notes: see `UPSTREAM_README.md`.
