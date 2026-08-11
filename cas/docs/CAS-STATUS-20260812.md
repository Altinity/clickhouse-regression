# CAS Testing Status — 11 August 2026

---

## 1. Status summary


| Area                                        | Status                                                                    | Run                                                                                       |
| ------------------------------------------- | ------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Jepsen fault injection, 60 min per scenario | 8/8 pass                                                                  | [31475969456](https://github.com/Altinity/clickhouse-regression/actions/runs/31475969456) |
| Aggregate functions on CAS                  | Pass                                                                      | [31505107385](https://github.com/Altinity/clickhouse-regression/actions/runs/31505107385) |
| Alter on CAS (single pool)                  | Pass, 6 skips                                                             | [31527469416](https://github.com/Altinity/clickhouse-regression/actions/runs/31527469416) |
| Tiered storage with CAS                     | Pass                                                                      | [31164138497](https://github.com/Altinity/clickhouse-regression/actions/runs/31164138497) |
| Dedicated CAS suite — replicated            | 8/10 scenarios pass                                                       | `cas/tests/`                                                                              |
| Dedicated CAS suite — distributed           | Pass                                                                      | `cas/tests/`                                                                              |
| ATTACH PARTITION into CAS from foreign pool | Fail                                                                      | 4.1                                                                                       |
| ATTACH PARTITION into CAS from local disk   | Fail                                                                      | [#2173](https://github.com/Altinity/ClickHouse/issues/2173)                               |
| Temporary tables on CAS                     | Untested, skipped — needs investigation                                   | §10 #3                                                                                    |
| `type=encrypted` wrapping CAS               | Unsupported — CREATE ok, INSERT `NOT_IMPLEMENTED`                         | 4.3                                                                                       |
| Static code audit follow-up                 | 131 findings; high 20/20 triaged by Filimonov; 72 still open (medium/low) | [#2031](https://github.com/Altinity/ClickHouse/issues/2031)                               |


---

## 2. Existing regression suites on CAS

### 2.1 Aggregate functions — [run 31505107385](https://github.com/Altinity/clickhouse-regression/actions/runs/31505107385)


|                       |                                                               |
| --------------------- | ------------------------------------------------------------- |
| Result                | Green                                                         |
| Scope                 | All aggregate functions, same results as on regular MergeTree |
| CAS-specific failures | None                                                          |


### 2.2 Alter — [run 31527469416](https://github.com/Altinity/clickhouse-regression/actions/runs/31527469416)

Run with `--cas`: CAS is set as the default MergeTree disk for the whole suite. Tested in a **single-pool** configuration only — every table lives on one shared CAS pool. Cross-pool and cross-disk variants are not covered here (see section 4).


| Sub-suite                  | Result | Scenarios (default, non-stress)                          |
| -------------------------- | ------ | -------------------------------------------------------- |
| `alter_move_partition`     | Pass   | ~6,850                                                   |
| `alter_replace_partition`  | Pass   | ~1,200 named, tens of thousands of inner parallel checks |
| `alter_attach_partition_1` | Pass   | ~4,500                                                   |
| `alter_attach_partition_2` | Pass   | ~50                                                      |


#### `alter_move_partition` — 3 modules


| Module                   | Operations and conditions                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `partition key`          | `ALTER TABLE … MOVE PARTITION … TO TABLE …` over a 28×28 matrix of integer partition-key expressions (`tuple()`, single columns, `%`, `intDiv`, tuples, column permutations); same-key and different-key pairs; invalid pairs must error (non-monotonic, non-subset, partially different); 4 source × 2 empty-destination MergeTree-family engines; replicated destination checked for consistency across clickhouse1–3; `DETACH TABLE` / `ATTACH TABLE` after the move |
| `partition key datetime` | Same, over 12×12 datetime key expressions (`toYYYYMMDD(time)` … `toSecond(time)`)                                                                                                                                                                                                                                                                                                                                                                                       |
| `move to self`           | Source table = destination table                                                                                                                                                                                                                                                                                                                                                                                                                                        |


#### `alter_replace_partition` — 13 modules


| Module                                      | Operations and conditions                                                                                                                                                                                                                                    |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `partition types`                           | `REPLACE PARTITION` with compact-only, wide-only, mixed, empty (lightweight delete) and no-parts (after `DROP PARTITION`) sources                                                                                                                            |
| `partition keys`                            | 28×28 integer partition-key pair matrix                                                                                                                                                                                                                      |
| `engines`                                   | 8×8 cross-product of MergeTree, Replacing, Summing, Collapsing, VersionedCollapsing, Graphite, Aggregating, ReplicatedMergeTree                                                                                                                              |
| `rbac`                                      | Privilege pairs on source and destination: none / `SELECT` / `INSERT` / `ALTER` / `ALTER TABLE`                                                                                                                                                              |
| `data integrity`                            | Source data retained after replace; non-existent partition in either direction; `system.parts` reflects the result                                                                                                                                           |
| `prohibited actions`                        | `FROM` a table function, JOIN, subquery, non-MergeTree engine, VIEW, MV, `remote`, `remoteSecure`; mismatched storage policy, partition key, ORDER BY, structure; syntax misuse (ORDER BY / PARTITION BY in statement, `INTO OUTFILE`, `FORMAT`, `SETTINGS`) |
| `temporary table`                           | temp→regular, temp→temp, regular→temp                                                                                                                                                                                                                        |
| `storage`                                   | Different local disks (expected fail); Distributed / sharded table (expected fail); replicated (allowed); MinIO S3 vs default (2×2); tiered vs default (2×2); partition previously moved to another disk (2×2)                                               |
| `corrupted partitions`                      | 0 / 1 / several / all parts corrupted on source, destination, or both (4×4) — **skipped under CAS**                                                                                                                                                          |
| `concurrent replace partitions`             | 100 parallel `REPLACE PARTITION` on one table                                                                                                                                                                                                                |
| `concurrent merges and mutations`           | Replace during a merge, and during a mutation, on an unrelated partition                                                                                                                                                                                     |
| `concurrent actions`                        | Replace running alongside ~30 other ALTERs: ADD / DROP / MODIFY / RENAME / COMMENT COLUMN, constraints, DETACH / ATTACH / MOVE PARTITION, FREEZE, CLEAR, plus a 100-iteration multi-action loop                                                              |
| `concurrent replace partitions on replicas` | 100 rounds × 3 parallel replaces on a 3-replica cluster: plain, secure, and sharded `ON CLUSTER`                                                                                                                                                             |


#### `alter_attach_partition_1` — 15 modules


| Module                              | Operations and conditions                                                                                                                                                                                                                                                                                            |
| ----------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `check simple attach partition`     | Baseline `ATTACH PARTITION`, 6 keys × 2×2 engines, `@Repeat(100)` → 2,400 runs                                                                                                                                                                                                                                       |
| `partition key`                     | `ATTACH PARTITION … FROM …` and `ATTACH PARTITION ID '…' FROM …`, 28 integer keys × 4 source × 2 destination engines, both ID variants; invalid pairs must error on monotonicity, subset, partially-different keys                                                                                                   |
| `partition key datetime`            | Full 12×12 datetime key cross-product                                                                                                                                                                                                                                                                                |
| `partition types`                   | Compact / wide / mixed / empty parts attached from the detached folder                                                                                                                                                                                                                                               |
| `conditions`                        | Mismatched structure, ORDER BY, PRIMARY KEY, storage policy, indices, projections                                                                                                                                                                                                                                    |
| `storage`                           | Distributed / sharded (expected fail); MinIO vs default (2×2); tiered vs default (2×2); attaching detached parts across disk types (2×2)                                                                                                                                                                             |
| `rbac`                              | Privileges for `ATTACH PARTITION FROM`, `ATTACH PARTITION`, `ATTACH PART`                                                                                                                                                                                                                                            |
| `table names`                       | Unicode and special-character table names, with and without partition ID                                                                                                                                                                                                                                             |
| `partition expression`              | Literal partition expressions, with and without ID                                                                                                                                                                                                                                                                   |
| `operations on attached partitions` | 7 follow-up operations after an attach: MOVE PARTITION, DETACH + ATTACH PARTITION, 8 multi-step attach/move chains, DROP PARTITION, REPLACE PARTITION, FREEZE, `UPDATE IN PARTITION`; 100 sampled key pairs per operation (500 for update)                                                                           |
| `part level`                        | Part-level semantics across 6 scenarios: level reset via DETACH PART / DETACH PARTITION × ATTACH PART / ATTACH PARTITION (7 engines each), level increment after merge (14 engines), replicated stress with 100 random operations, rejection of an over-high part level (4×7×2), reset at the legacy max level (7×7) |
| `temporary table`                   | Attach detached into temporary tables (2 table types × 7 engines); attach-from across temp/regular combinations (3×3 table types × 7×7 engine pairs, 100 random samples)                                                                                                                                             |
| `corrupted partitions`              | Corrupted parts on attach-from, attach-detached, and single-part attach (4×4 each)                                                                                                                                                                                                                                   |
| `replica sanity`                    | Adding and removing replicas in parallel with ongoing inserts                                                                                                                                                                                                                                                        |


#### `alter_attach_partition_2` — 2 modules


| Module                      | Operations and conditions                                                                                                                     |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `add_remove_replica`        | `ATTACH PARTITION … FROM …` while replicas are dynamically added and removed, 7 source × 7 destination Replicated engine pairs = 49 scenarios |
| `restart clickhouse server` | Attach partitions, restart the server, verify the data is still readable                                                                      |


#### CAS exclusions

"Alter passes on CAS" holds only with these six skipped, as declared in `alter/regression.py`:


| Skipped path                                                                           | Reason                                                                                  |
| -------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| `/alter/attach partition/part 1/corrupted partitions`                                  | Requires local part files under `/var/lib/clickhouse`                                   |
| `/alter/replace partition/corrupted partitions`                                        | Same                                                                                    |
| `/alter/attach partition/part 1/part level/too high level`                             | Renames detached parts on the local filesystem                                          |
| `/alter/attach partition/part 1/part level/part levels user example`                   | Same                                                                                    |
| `/alter/attach partition/part 1/operations on attached partitions/multiple operations` | Chained attach → {attach|move} × 3 sequences across different partition keys            |
| `/alter/attach partition/part 1/temporary table`                                       | Skipped under CAS; recorded reason cites #2173 (wrong defect) — investigate, see §10 #3 |


Everything else — including cross-engine, RBAC, prohibited-action, concurrency, replica, and part-level coverage — runs unmodified on CAS.

### 2.3 Tiered storage with CAS — [run 31164138497](https://github.com/Altinity/clickhouse-regression/actions/runs/31164138497)


|               |                                                                                                                                                     |
| ------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| Result        | Green                                                                                                                                               |
| Configuration | Cold tier on CAS, hot tiers on local disk                                                                                                           |
| Issue found   | FREEZE backup path on CAS is `shadow/...`, not `/shadow/...` as on other disk types. Fixed test-side; path shape difference remains (§10 #4) |


---

## 3. Dedicated CAS suite (`cas/tests/`)

10 scenarios written; 8 pass. Every test asserts all 3 replicas agree by checksum and no permanent errors remain in the replication queue.


| Scenario                                                  | Result        |
| --------------------------------------------------------- | ------------- |
| Replicated tables converge across 3 replicas, shared pool | Pass          |
| Cross-pool fetch falls back to byte copy                  | Pass          |
| ATTACH PARTITION FROM, one pool                           | Pass          |
| REPLACE PARTITION, one pool                               | Pass          |
| DETACH / ATTACH / DROP DETACHED partition                 | Pass          |
| MOVE PARTITION between replicated tables                  | Pass          |
| Distributed table fan-out across CAS shards               | Pass          |
| ON CLUSTER DDL for CAS tables                             | Pass          |
| ATTACH PARTITION from foreign CAS pool                    | Fail, see 4.1 |
| ATTACH PARTITION from local disk                          | Fail, see 4.2 |


---

## 4. Defects

### 4.1 ATTACH PARTITION into CAS from a different pool


|                          |                                                                                                                                                      |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Command                  | `ALTER TABLE dst ATTACH PARTITION p FROM src`, `src` in a different CAS pool                                                                         |
| Error                    | Code 48 `NOT_IMPLEMENTED`: `The operation 'generateObjectKeyForPath' is not implemented for a content-addressed disk`                                |
| Root cause               | `notYet("generateObjectKeyForPath")`, `ContentAddressedTransaction.cpp:531`                                                                          |
| Correct behaviour exists | `REPLACE PARTITION` on the same tables rejects cleanly: Code 36 `Could not clone and load part '...' because disk does not belong to storage policy` |
| Side effects             | None, fails immediately, both tables untouched                                                                                                       |
| Issue                    | TBD                                                                                                                                                  |


### 4.2 ATTACH PARTITION into CAS from a local disk


|                 |                                                                                                                                                                             |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Command         | `ALTER TABLE dst ATTACH PARTITION p FROM src`, `src` on ordinary local disk                                                                                                 |
| Error           | Code 210 `NETWORK_ERROR`: `CAS write could not be committed (promote: ref 'tmp_replace_from_1_1_1_0' already names a different committed manifest — refusing to overwrite)` |
| Failure point   | After all partition files are copied into CAS, at commit                                                                                                                    |
| Side effects    | **Each failed attempt leaves a full copy of the partition in the pool**, reclaimable only by GC                                                                             |
| Retry behaviour | Temp ref name derives from partition + per-process counter, so each retry mints the next index and fails identically                                                        |
| Manual GC       | Not a workaround, tested; next attempt fails the same way                                                                                                                   |
| Issue           | [Altinity/ClickHouse#2173](https://github.com/Altinity/ClickHouse/issues/2173)                                                                                              |


### 4.3 `type=encrypted` wrapping a CAS disk — unsupported


|                |                                                                                                                              |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Configuration  | `type=encrypted` disk whose inner disk is `metadata_type=content_addressed` (CAS)                                            |
| CREATE TABLE   | Succeeds when `storage_policy` points at the encrypted disk                                                                  |
| INSERT         | Fails: `Code: 48 NOT_IMPLEMENTED` — `Autocommit writes are not supported for content part files on a content-addressed disk` |
| Classification | Known unsupported composition / feature gap, not a silent corruption bug                                                     |


Developer response (CAS owner):

Support may be possible later, but neither the code path nor the design is obvious. Until then: document as unsupported; prefer fail-fast at disk/`CREATE TABLE` over INSERT.

---

## 5. Open question: does relink actually avoid byte transfer?

CAS's stated benefit is that a replica adopts a manifest already in the shared pool instead of uploading its own copy. Measured result contradicts that.

Counters from `system.events`, before/after fetch:


| Scenario                                   | Writer uploads | Receiver uploads | Receiver adoptions | Receiver dedup |
| ------------------------------------------ | -------------- | ---------------- | ------------------ | -------------- |
| Lagging follower catch-up                  | 8              | 10               | 4                  | none           |
| FETCH PART / FETCH PARTITION into detached | 10             | 12               | 4                  | none           |


Expected receiver uploads ≈ 0.


|              |                                                                                                            |
| ------------ | ---------------------------------------------------------------------------------------------------------- |
| Hypothesis A | Relink does not engage for freshly written data; replica falls back to upload                              |
| Hypothesis B | The counters measured do not mean what was assumed; the test is wrong                                      |
| Audit note   | Static audit independently flagged relink as having no test coverage anywhere                              |
| Next step    | Count actual PUT requests at the object store during replica catch-up instead of reading internal counters |


---

## 6. Jepsen

### 6.1 Run


|                       |                                                                                                                                                             |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Run                   | [31475969456](https://github.com/Altinity/clickhouse-regression/actions/runs/31475969456), x86                                                              |
| Verdict               | **8 successes, 0 failures, 0 unknown, 0 crashed**                                                                                                           |
| Window                | 2026-08-11, 09:06 → 17:18 GMT, 8 h 30 m wall clock                                                                                                          |
| Duration per scenario | **60 minutes**, one scenario per nemesis (`--test-count 8`)                                                                                                 |
| Parameters            | concurrency 12, target rate 10 ops/s                                                                                                                        |
| Topology              | 3 ClickHouse nodes + 1 Keeper, Docker; object store RustFS; single shared CAS pool                                                                          |
| Workload              | `set` — insert unique integers into ReplicatedMergeTree on CAS policy, `insert_quorum = 2`, `async_insert = 0`; then `SYSTEM SYNC REPLICA` + final `SELECT` |
| Checks                | No lost writes (acknowledged insert missing), no unexpected values (value never written)                                                                    |
| Full report           | `cas/docs/CAS-JEPSEN-REPORT-20260811.md`                                                                                                                    |


### 6.2 Results per nemesis


| Nemesis                    | Fault                                                      | Attempted   | Acknowledged | Recovered | Lost  | Unexpected | Valid   |
| -------------------------- | ---------------------------------------------------------- | ----------- | ------------ | --------- | ----- | ---------- | ------- |
| `random-node-hammer-time`  | SIGSTOP one node, then SIGCONT                             | 35,925      | 19,150       | 1         | **0** | **0**      | yes     |
| `bridge-partitioner`       | Two nodes isolated from each other, both see a bridge node | 35,879      | 18,696       | 0         | **0** | **0**      | yes     |
| `all-nodes-hammer-time`    | SIGSTOP all nodes, then SIGCONT                            | 35,646      | 13,850       | 0         | **0** | **0**      | yes     |
| `random-node-killer`       | Kill ClickHouse on one node, restart                       | 35,842      | 12,110       | 7         | **0** | **0**      | yes     |
| `blind-node-partitioner`   | Victim cannot send, others can send to it                  | 35,829      | 6,941        | 0         | **0** | **0**      | yes     |
| `simple-partitioner`       | Split cluster into two random halves                       | 35,902      | 5,866        | 1         | **0** | **0**      | yes     |
| `blind-others-partitioner` | Reverse asymmetry of the above                             | 35,886      | 5,400        | 0         | **0** | **0**      | yes     |
| `all-nodes-killer`         | Kill ClickHouse on all nodes at once, restart              | 35,612      | 2,378        | 12        | **0** | **0**      | yes     |
| **Total**                  |                                                            | **286,521** | **84,391**   | **21**    | **0** | **0**      | **8/8** |


29% of attempted inserts acknowledged overall; 6.7% under `all-nodes-killer`. Expected: with `insert_quorum = 2` on 3 nodes, any nemesis removing 2 nodes makes writes correctly unavailable. Nemesis op counts confirm faults fired: 1,420–1,436 per partition scenario, 262–266 per kill scenario, 1,302 for `all-nodes-hammer-time`.

### 6.3 Server logs, harshest scenario (`all-nodes-killer`, node 172.18.0.4, 1 h)


|                                                                           |                                                                                            |
| ------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| Fatal / logical errors / sanitizer reports / segfaults / `std::terminate` | None                                                                                       |
| 843                                                                       | `Quorum for previous write has not been satisfied yet` (Code 286)                          |
| 363                                                                       | `Another quorum insert has been already started` (Code 286)                                |
| 174                                                                       | `Number of alive replicas (1) is less than requested quorum (2/3)` (TOO_FEW_LIVE_REPLICAS) |


All errors are correct refusals to acknowledge writes that cannot meet the durability contract.

### 6.4 Proven / not covered


| Proven                                                                                    | Not covered                                                                                        |
| ----------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| No acknowledged write lost under node kills, freezes, 4 partition shapes incl. asymmetric | GC and pool integrity — no `ca-fsck`, no orphan/dangling-ref check after faults                    |
| No fabricated data                                                                        | Relink efficiency — safety only, byte transfer not measured                                        |
| Replicas converge after healing                                                           | One workload only (`set`): no read-under-fault, no DDL, no mutation, no OPTIMIZE, no schema change |
| Server survives repeated hard kills on CAS                                                | Single pool, single disk — the configuration where known defects live                              |
| Quorum semantics honoured on CAS as on ordinary disk                                      | No S3-level fault injection; RustFS healthy throughout; x86 only, 1 run per nemesis                |


---

## 7. Static code audit


|                |                                                                                                                                                                                                         |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Tracking issue | [Altinity/ClickHouse#2031](https://github.com/Altinity/ClickHouse/issues/2031)                                                                                                                          |
| Re-run         | 11 August, 22 areas, none clean                                                                                                                                                                         |
| Findings       | 131 distinct (`CAS-###`); **high 20/20 checked** (Filimonov triage: ~6 fixed, rest by-design / not-a-bug / out-of-scope / partial / wontfix); overall 59 checked, **72 still open** (mostly medium/low) |
| Reports        | `cas/docs/cas-audit-rerun-20260811/reports/`                                                                                                                                                            |


---

## 8. Coverage matrix

| Workstream | State |
|---|---|
| Dedicated CAS tests — replicated | 8/10 pass |
| Dedicated CAS tests — distributed / sharded | Pass |
| Dedicated CAS tests — one disk per table vs shared disk | Not started |
| Aggregate functions on CAS | Green, in CI |
| Alter on CAS, single pool | Green, in CI |
| Tiered storage with CAS | Green, in CI |
| `lightweight_delete`, `atomic_insert`, `selects` on CAS | Planned (§9) |
| Jepsen | 8/8 green; no post-run pool check |
| Requirements spec (SRS-048) | Written, tests reference it |
| Soak testing | Ported into repo; not in CI |
| S3 dependency review | Doc exists; listing-safety audit not done |
| Static audit re-run | ToDo on PR #2159 |
| Stress testing | Not started |
| CI automation | `tiered_storage_cas`, aggregate `--cas`, alter `--cas` wired |
| `type=encrypted` over CAS | Unsupported; draft in `ISSUE-DRAFT-encrypted-over-cas.md` |


---

## 9. Planned suites on CAS

### 9.1 `lightweight_delete`


|                        |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Priority               | High — highest CAS relevance of the three                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| Scale                  | ~125 scenarios + 11 outlines across 38 features; scenarios multiply by 7 MergeTree and 7 Replicated engine variants                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| Setup                  | 3 nodes, ZooKeeper + Keeper, MinIO available; `replicated_cluster` (1 shard × 3 replicas) and `sharded_cluster` (3 shards)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| What it tests          | `DELETE` correctness (basic, specific rows, invalid WHERE, immediate removal, multi-delete limits, compatibility); alter after delete (detach/drop/attach/replace partition, column ops); projections; concurrency (concurrent delete, concurrent alter+delete, random concurrent alter); replication (replicated tables, replicated concurrent deletes, replication queue, distributed tables); TTL (column TTL, tiered-storage TTL, delete+TTL); storage (S3 disk, multi-disk volume, encrypted disk, disk space and lack of disk space, efficient physical data removal, drop empty part, backup); resilience (hard restart, load, ZooKeeper load, performance, ontime dataset); views |
| Why it matters for CAS | Exercises mutation and part-rewrite paths on object storage, physical data removal, drop-empty-part, and tiered/multi-disk policies — i.e. exactly the delete-and-reclaim paths where the audit's storage-leak findings sit                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| Caveats                | Most tests default to local disk unless the storage policy is overridden; several storage/replication features are module-level xfail ("engine type not supported")                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |


### 9.2 `atomic_insert`


|                        |                                                                                                                                                                                                                                                                                                                                                                                       |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Priority               | Medium                                                                                                                                                                                                                                                                                                                                                                                |
| Scale                  | ~22 scenarios + 6 outlines across 8 features; 2 engines by default (MergeTree, ReplicatedMergeTree), 14 under `--stress`                                                                                                                                                                                                                                                              |
| Setup                  | 4 nodes, ZooKeeper + Keeper, no MinIO, local disk only today; cluster `ShardedAndReplicated` (3 shards, nodes 1, 2, 3+4); experimental transactions enabled                                                                                                                                                                                                                           |
| What it tests          | All-or-nothing rollback on partial insert failure; atomic-insert settings per engine; dependent tables (MV chains, live/window views, engine mismatch, circular deps); atomic insert through Distributed with shard/replica/Keeper failures; user-rights failures mid-insert; explicit `BEGIN`/`COMMIT`/`ROLLBACK` with parallel failing inserts; SIGKILL during large random inserts |
| Why it matters for CAS | Insert rollback and SIGKILL recovery test whether aborted CAS writes leave staged blobs or half-committed manifests behind                                                                                                                                                                                                                                                            |
| Caveats                | Suite has no storage-policy variants; requires overriding the default policy to CAS to be meaningful                                                                                                                                                                                                                                                                                  |


### 9.3 `selects`


|                        |                                                                                                                                                                                                                                                                                                                |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Priority               | Low                                                                                                                                                                                                                                                                                                            |
| Scale                  | 66 scenarios + 7 outlines in 4 active sub-features; 17 engine types; hundreds to ~1000+ combinatorial examples                                                                                                                                                                                                 |
| Setup                  | 3 nodes, ZooKeeper + Keeper, no MinIO, local disk; clusters `simple`, `replicated`, `sharded`, `sharded_replicated`                                                                                                                                                                                            |
| What it tests          | `force_select_final` / `FINAL` semantics: count, DISTINCT, GROUP BY, ORDER BY, LIMIT, LIMIT BY, PREWHERE, WHERE, AS, JOIN, subqueries, with and without explicit FINAL and with/without the analyzer; aliased columns; parallel SELECTs under concurrent inserts/deletes/updates; FINAL setting access control |
| Why it matters for CAS | Read-path regression check only; the `concurrent` sub-feature is the one part that touches CAS read/write interleaving                                                                                                                                                                                         |
| Caveats                | Pure query-semantics suite, storage backend should not affect results; lowest expected yield of the three                                                                                                                                                                                                      |


---

## 10. Next steps

| # | Action |
|---|---|
| 1 | Relink: count object-store PUTs on replica catch-up (§5) |
| 2 | File 4.1; link to #2173 (draft ready) |
| 3 | Temp tables on CAS: un-skip alter path; fix wrong #2173 skip reason |
| 4 | FREEZE on CAS: freeze-partition + path shape `shadow/...` vs `/shadow/...` (§2.3) |
| 5 | FORGET PARTITION Code 716 after drop — likely test/Keeper; verify |
| 6 | Jepsen: post-scenario `ca-fsck` + blob/ref counts |
| 7 | S3 listing-safety audit; record model/method on every report |
| 8 | Jepsen: S3 fault injection via soak fault proxy |
| 9 | Start `lightweight_delete`, `atomic_insert`, `selects` on CAS (§9) |
| 10 | File encrypted-over-CAS unsupported (4.3); decide fail-fast vs support (decision 3) |


---

## 11. Decisions needed


| # | Question | Consequence |
|---|---|---|
| 1 | Is importing partitions into CAS from another disk or pool in scope? | Yes → 4.1 and 4.2 are bugs to fix. No → clean rejection message + documented limitation |
| 2 | Are temporary tables in scope on CAS? | Currently skipped and untested; the answer decides whether to un-skip or document as unsupported (§10 #3) |
| 3 | Is `type=encrypted` wrapping CAS in scope, or permanently out of scope in favour of S3 SSE? | In scope → design what is encrypted + implement. Out of scope → document + fail-fast at create (4.3) |


---

