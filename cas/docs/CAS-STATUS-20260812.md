# CAS Testing Status — 12 August 2026

## 1. Summary

| Area | Status | Link |
|---|---|---|
| Jepsen (60 min × 8 nemeses) | 8/8 pass | [31475969456](https://github.com/Altinity/clickhouse-regression/actions/runs/31475969456) |
| Aggregate functions on CAS | Pass, in CI | [31505107385](https://github.com/Altinity/clickhouse-regression/actions/runs/31505107385) |
| Alter on CAS (single pool) | Pass, 6 skips, in CI | [31527469416](https://github.com/Altinity/clickhouse-regression/actions/runs/31527469416) |
| Tiered storage with CAS | Pass, in CI | [31164138497](https://github.com/Altinity/clickhouse-regression/actions/runs/31164138497) |
| Dedicated suite (`cas/tests/`) | 8/10 pass; distributed pass | §3 |
| ATTACH from foreign CAS pool | Fail | §4.1 |
| ATTACH from local disk | Fail | [#2173](https://github.com/Altinity/ClickHouse/issues/2173) |
| Temporary tables | Skipped / untested | §7 #3 |
| `type=encrypted` over CAS | Unsupported | §4.3 |
| Static audit | High 20/20 triaged; 72 open (med/low) | [#2031](https://github.com/Altinity/ClickHouse/issues/2031) |

---

## 2. Regression suites on CAS

**Aggregate functions** — green; same results as regular MergeTree.

**Alter** (`--cas`, one shared pool only — not cross-pool/cross-disk):

| Sub-suite | Result | Scale (default) |
|---|---|---:|
| `alter_move_partition` | Pass | ~6.8k |
| `alter_replace_partition` | Pass | ~1.2k named + large parallel inner checks |
| `alter_attach_partition_1` | Pass | ~4.5k |
| `alter_attach_partition_2` | Pass | ~50 |

Coverage includes partition-key matrices (int + datetime), engines, RBAC, storage policies, concurrency, replicas, part levels, post-attach ops (move/detach/drop/replace/freeze/update).

Skipped under CAS (`alter/regression.py`):

| Path | Reason |
|---|---|
| attach/replace `corrupted partitions` | Needs local part files |
| attach `part level/too high level`, `part levels user example` | Renames detached parts on local FS |
| attach `operations…/multiple operations` | FREEZE/UNFREEZE hardlinks unsupported on CAS |
| attach `temporary table` | [#2173](https://github.com/Altinity/ClickHouse/issues/2173) |

**Tiered storage** — cold on CAS, hot local; green. FREEZE works; CAS reports disk-relative paths (`shadow/...`) instead of a local `…/shadow/` tree — test adjusted, not a functional bug.

---

## 3. Dedicated suite (`cas/tests/`)

All scenarios check 3-replica checksum agreement and empty replication queue.

| Scenario | Result |
|---|---|
| Replicated converge, shared pool | Pass |
| Cross-pool fetch → byte copy | Pass |
| ATTACH / REPLACE / MOVE / DETACH (one pool) | Pass |
| Distributed fan-out; ON CLUSTER DDL | Pass |
| ATTACH from foreign CAS pool | Fail → §4.1 |
| ATTACH from local disk | Fail → §4.2 |

---

## 4. Defects

### 4.1 ATTACH from another CAS pool

`ATTACH PARTITION … FROM …` → Code 48 `NOT_IMPLEMENTED` (`generateObjectKeyForPath`). Fails immediately, no side effects. Same setup: `REPLACE PARTITION` rejects cleanly (Code 36, disk not in policy). Issue TBD (draft ready).

### 4.2 ATTACH from local disk → [#2173](https://github.com/Altinity/ClickHouse/issues/2173)

Fails at commit: Code 210 `NETWORK_ERROR`, unique-ref collision on `tmp_replace_from_*`. Files are already copied into the pool; **each retry leaves another full copy** (GC only). Manual GC does not help retries.

### 4.3 Encrypted disk over CAS — unsupported

CREATE ok; INSERT → Code 48 `NOT_IMPLEMENTED` (autocommit). Owner: maybe later; until then document + prefer fail-fast at create. Draft: `ISSUE-DRAFT-encrypted-over-cas.md`.

---

## 5. Relink — open question

Claim: replicas adopt shared manifests instead of re-uploading. `system.events` on catch-up / FETCH still show receiver uploads ≫ 0 (expected ≈ 0). Either relink is not kicking in, or the counters are the wrong signal. Audit also noted no relink coverage. **Next:** count real object-store PUTs during catch-up.

---

## 6. Jepsen

[Run 31475969456](https://github.com/Altinity/clickhouse-regression/actions/runs/31475969456) — x86, 3 CH + Keeper, RustFS, one CAS pool. Workload: `set` inserts into ReplicatedMergeTree, `insert_quorum=2`. **8/8 valid, 0 lost, 0 unexpected.** Full report: `CAS-JEPSEN-REPORT-20260811.md`.

| Nemesis | Fault | Ack | Lost | Unexpected |
|---|---|---:|---:|---:|
| `random-node-hammer-time` | SIGSTOP one node | 19,150 | 0 | 0 |
| `bridge-partitioner` | bridge partition | 18,696 | 0 | 0 |
| `all-nodes-hammer-time` | SIGSTOP all | 13,850 | 0 | 0 |
| `random-node-killer` | kill one node | 12,110 | 0 | 0 |
| `blind-node-partitioner` | one-way blind | 6,941 | 0 | 0 |
| `simple-partitioner` | split halves | 5,866 | 0 | 0 |
| `blind-others-partitioner` | reverse blind | 5,400 | 0 | 0 |
| `all-nodes-killer` | kill all | 2,378 | 0 | 0 |
| **Total** | | **84,391** / 286,521 attempted | **0** | **0** |

Low ack rate under hard faults is expected with quorum 2/3. Harsh-case logs: only quorum / too-few-replicas refusals; no fatals.

**Not covered:** pool `ca-fsck` after faults; relink efficiency; workloads beyond `set`; S3-level faults; cross-pool/cross-disk (where known bugs are).

---

## 7. Coverage & next steps

| Done | Not yet |
|---|---|
| Dedicated suite (mostly), agg/alter/tiered in CI, Jepsen 8/8, SRS-048 | Per-table disks, soak in CI, stress, LWD / atomic_insert / selects on CAS, S3 listing audit, Jepsen fsck + S3 faults |

| # | Next |
|---|---|
| 1 | Relink: count object-store PUTs on catch-up (§5) |
| 2 | File §4.1; link to #2173 (draft ready) |
| 3 | Temp tables: un-skip alter path; fix skip reason if wrong |
| 4 | Confirm alter FREEZE path under `--cas` |
| 5 | FORGET PARTITION Code 716 after drop — likely test/Keeper |
| 6 | Jepsen: post-run `ca-fsck` + blob/ref counts |
| 7 | S3 listing-safety audit |
| 8 | Jepsen: S3 fault injection (soak fault proxy) |
| 9 | Run `lightweight_delete`, `atomic_insert`, `selects` on CAS |
| 10 | File encrypted-over-CAS unsupported; decide fail-fast vs later support |

Planned suites briefly: **LWD** (high — mutations/reclaim), **atomic_insert** (medium — abort/rollback leftovers), **selects** (low — mostly query semantics; concurrent sub-feature matters most). All need `--cas` / default-policy override.

---

## 8. Decisions needed

| # | Question | If yes / no |
|---|---|---|
| 1 | Import partitions into CAS from another disk/pool? | Fix §4.1–4.2 / clean reject + document |
| 2 | Temporary tables on CAS? | Un-skip / document unsupported |
| 3 | `encrypted` over CAS, or S3 SSE only? | Implement / fail-fast at create |

---

## Sources

| | |
|---|---|
| Suite | `cas/tests/` |
| Jepsen | `cas/docs/CAS-JEPSEN-REPORT-20260811.md` |
| Issue drafts | `ISSUE-DRAFT-cas-cross-pool-attach.md`, `ISSUE-DRAFT-cas020-cross-disk-attach.md`, `ISSUE-DRAFT-encrypted-over-cas.md` |
| Audit | `cas/docs/cas-audit-rerun-20260811/reports/`, [#2031](https://github.com/Altinity/ClickHouse/issues/2031) |
| Requirements | `cas/requirements/requirements.md` (SRS-048) |
| Reports index | https://altinity-internal-test-reports.s3.amazonaws.com/index.html#reports/cas_testing_reports/ |
