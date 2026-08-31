# Usability Audit: ClickHouse CAS (PR #2159)

**Scope:** Content-addressed storage (`metadata_type = cas`) at PR #2159 @ `ceee42c51a06cb05e2c9a2d811ef7e1726825552`, operator SQL/docs surface (`docs/en/antalya/cas/`, `SYSTEM CAS *`)
**Persona:** Operator / DBA
**Environment:** Replicated or multi-server pool on a shared object-store prefix; recommended cache disk in front of the raw CAS disk.

## Primary flows (ranked by expected usage)
1. Configure a CAS disk (`cas_server_root_id` + `metadata_type = cas`), `CREATE TABLE` / `INSERT` / `SELECT` on the storage policy. *(most common; [quick-start](docs/en/antalya/cas/quick-start.md))*
2. Day-2 health: `system.cas_mounts` / `system.cas_gc_log` and `SYSTEM CAS GC RUN|STOP|START`.
3. Integrity check: `SYSTEM CAS FSCK` (live) or `clickhouse-disks cas-fsck` (offline).
4. Tiered migration: `ALTER TABLE ... MOVE PARTITION ... TO DISK` onto/off the cached CAS volume.
5. Retire a member or a node-local disk: `SYSTEM CAS DROP POOL MEMBER` / `SYSTEM CAS FORGET`.

## Issues

Issues are grouped by the primary flow they affect. Within each group, order by severity (blocker → low).

### Flow 1: First table on a CAS disk

#### 1.1 `SYSTEM RELOAD CONFIG` does not apply any `cas_*` setting
- **Symptom:** XML is changed and reload succeeds; `cas_gc_enabled`, `cas_gc_interval_sec`, and cache budgets stay at mount-time values with no warning (`IMetadataStorage.h:365-368`; `DiskObjectStorage.cpp:978-984`; no `ContentAddressedMetadataStorage::applyNewSettings`). Removing the disk from config leaves the mount lease renewing until restart.
- **Trigger:** Normal config change / rolling reload.
- **Signal quality:** Silent.
- **Severity:** Medium.
- **Recovery:** Restart the server (self-service once known).

#### 1.2 `DiskEncrypted` over CAS is accepted at config and fails at the first part write
- **Symptom:** Server starts; `INSERT`/merge raises `NOT_IMPLEMENTED` (`DiskEncrypted` does not forward `isContentAddressed`).
- **Trigger:** Operator wraps the CAS disk in encryption, following the usual encrypted-disk pattern.
- **Signal quality:** Confusing (late, generic).
- **Severity:** Medium.
- **Recovery:** Self-service: remove the encryption wrapper and recreate the table on a plain CAS volume.

### Flow 2: Day-2 health and GC verbs

#### 2.1 `is_leader = 0` and `last_success_age_seconds = 0` do not name the real state
- **Symptom:** Fresh mount, follower, GC STOP, and "just succeeded" are not separable. Column comment says `last_success_age_seconds` is `0` if never led (`CasGcScheduler.h:128`); `gcHealth` also leaves it `0` when `last_success_ms == 0` and when a success is less than one second old (`CasGcScheduler.cpp:397-403`). `is_leader` is NULL on peer rows (`StorageSystemContentAddressedMounts.cpp:194-209`). Debugging copy treats `is_leader = 0` as "this node never reclaims" (`docs/en/antalya/cas/operations/debugging.md:65`).
- **Trigger:** Reading `system.cas_mounts` after mount, after `GC STOP`, or immediately after a led round.
- **Signal quality:** Confusing.
- **Severity:** Medium.
- **Recovery:** Cross-check `system.cas_gc_log` `Finish.outcome` and whether `GC STOP` was issued; engineer required under incident pressure.

#### 2.2 `SYSTEM CAS GC RUN` with no disk name runs twice on a cache-wrapped pool
- **Symptom:** Two result rows (`cas` and `cas_cache`) and two sequential rounds on the same metadata storage (`InterpreterSystemQuery.cpp:2550-2558`; `DiskObjectStorageCache.cpp:29-31` shares the CA store).
- **Trigger:** Operator follows the parser's optional-disk form (`SYSTEM CAS GC RUN`).
- **Signal quality:** Confusing.
- **Severity:** Medium.
- **Recovery:** Self-service: always pass the raw CAS disk name.

#### 2.3 Covered-log cleanup silently stops when any catalog row in the pool changes
- **Symptom:** `pending_reclaim` / leftover ref objects persist across rounds that still report `Success`/`Deferred`. Stop reason is `LOG_DEBUG` only (`CasGc.cpp:3290-3298`).
- **Trigger:** Normal CREATE/DROP on any other table in the same pool during the leader's cleanup phase.
- **Signal quality:** Silent.
- **Severity:** Medium.
- **Recovery:** Runbook: expect many rounds under DDL churn; do not treat one `GC RUN` as drained.

### Flow 3: Integrity (FSCK)

#### 3.1 `SYSTEM CAS FSCK` cannot be cancelled and has no timeout
- **Symptom:** Query holds `lifecycle_mutex` for the entire scan (`ContentAddressedMetadataStorage.cpp:1122-1134`) and calls `runFsck` with no deadline (`CasFsck.cpp:1128-1134`). `KILL QUERY` / `max_execution_time` do not stop it. Concurrent `GC STOP` / `FORGET` wait. Docs tell the operator to raise `--timeout` on the CLI form and admit the SQL form has no override (`docs/en/antalya/cas/operations/troubleshooting.md:24`).
- **Trigger:** FSCK of a large pool from SQL, the path the debugging guide leads with.
- **Signal quality:** Silent (looks like a hung query).
- **Severity:** High.
- **Recovery:** Engineer required (wait it out or restart).

#### 3.2 SQL FSCK always reports `stale_edge = 0`
- **Symptom:** Column is present so it looks checked; the summary scan never fills it (`InterpreterSystemQuery.cpp:2480-2483`).
- **Trigger:** `SYSTEM CAS FSCK` without switching to `clickhouse-disks cas-fsck --detail`.
- **Signal quality:** Confusing.
- **Severity:** Low.
- **Recovery:** Self-service: use the offline `--detail` applet.

### Flow 4: MOVE PARTITION onto / off CAS

#### 4.1 Same-type object-storage copy off CAS writes envelope bytes, not payload
- **Symptom:** `getStorageObjects` returns the blob key with payload length and no header offset (`ContentAddressedMetadataStorage.cpp:1936-1940`). `DiskObjectStorage::copyFile` uses server-side copy when `DataSourceDescription` matches (`DiskObjectStorage.cpp:300-308` → `copyFileImpl` at `DiskObjectStorageTransaction.cpp:522-551`). Destination file is envelope+payload. MOVE to a *local* disk uses `readFile`/`prepareRead` and is safe (`IDisk.cpp:75-77`).
- **Trigger:** `BACKUP` to S3 on the same host, or `MOVE PARTITION` / `copyFile` onto another object-storage disk with the same description. Documented rollback to `local_disk` is the safe path.
- **Signal quality:** Silent if checksums are not checked; loud if they are.
- **Severity:** High.
- **Recovery:** Engineer required: restore from a payload-correct copy; do not use same-type server-side copy as the rollback.

#### 4.2 Policy disk name is the cache, not the raw CAS disk
- **Symptom:** `MOVE PARTITION ... TO DISK 'cas'` is refused (`UNKNOWN_DISK` / already on `cas_cache`) (`docs/en/antalya/cas/operations/migration.md:157-161`).
- **Trigger:** Operator names the disk they configured as `metadata_type = cas`.
- **Signal quality:** Confusing (error names the cache disk).
- **Severity:** Low.
- **Recovery:** Self-service: use the cache volume name from the policy.

### Flow 5: Decommission / FORGET

#### 5.1 `DROP POOL MEMBER` on a path-prefix id deletes a nested live member
- **Symptom:** `validateServerRootId` allows slashes (`CasServerRoot.h:76-105`). Decommission selects namespaces with `ns == srid || ns.starts_with(srid + "/")` (`CasDecommission.cpp:146-151`) and LISTs `cas/manifests/<srid>/` and `roots/<srid>/` (`CasLayout.h:422-431`), which include `a/b`.
- **Trigger:** Hierarchical ids (`dc1` and `dc1/host1`) plus `SYSTEM CAS DROP POOL MEMBER 'dc1' FROM DISK 'cas'`.
- **Signal quality:** Silent (command reports the child's namespaces as the victim's).
- **Severity:** High.
- **Recovery:** Engineer required; those namespaces and debris are already dropped.

#### 5.2 `FORGET` and `DROP POOL MEMBER` look like twins and are not
- **Symptom:** `FORGET` is node-local force-Vanish and "erasure was NOT verified" (`InterpreterSystemQuery.cpp:2656-2660`). `DROP POOL MEMBER` fences one `server_root_id` pool-wide and drains its namespaces (`docs/en/antalya/cas/operations/migration.md:164-175`). Both are `SYSTEM CAS` + a disk name.
- **Trigger:** Operator retiring a host picks the shorter verb.
- **Signal quality:** Confusing.
- **Severity:** Medium.
- **Recovery:** Runbook: `FORGET` only for a stuck local disk; use `DROP POOL MEMBER` only after `system.cas_mounts` shows the member dead.

### Cross-flow issues (apply to all primary flows)

#### X.1 Hierarchical `cas_server_root_id` is documented as a path and never checked for prefix overlap
- **Symptom:** Docs call the id a "clean relative path" that roots four subtrees (`docs/en/antalya/cas/architecture/mounts-and-leases.md:15-33`). No mount-time refusal when `a` and `a/b` both exist. Feeds #5.1.
- **Trigger:** Using `{cluster}/{replica}` next to a shorter cluster-level id.
- **Signal quality:** Silent.
- **Severity:** Medium.
- **Recovery:** Self-service: use a single path segment (`{replica}`) and never nest ids.

## Readiness verdict
- **Flow 1 (first table) in isolation:** ready with caveats, because of #1.1 and #1.2.
- **Flow 2 (health + GC verbs) in isolation:** ready with caveats, because of #2.1, #2.2, and #2.3.
- **Flow 3 (FSCK) in isolation:** ready with caveats, because of #3.1 (use the CLI with `--timeout` instead of SQL on large pools).
- **Flow 4 (MOVE PARTITION) in isolation:** ready with caveats, because of #4.1 (local-disk rollback is safe; same-type object-storage copy is not).
- **Flow 5 (decommission) in isolation:** ready with caveats, because of #5.1 and #5.2; not ready if any `server_root_id` can be a prefix of another.
- **Overall in production (network blips, concurrent admin ops, scale):** ready with caveats (guardrails required), because of #3.1, #4.1, #5.1, #2.3, and #1.1.

## Operator guidance (until fixes land)
- Give every replica a single-segment unique `cas_server_root_id` (`{replica}`). Never use an id that is a prefix of another (#5.1, X.1).
- Do not run `SYSTEM CAS DROP POOL MEMBER` on a shorter path than a live member's id (#5.1). Confirm the member is not `live` in `system.cas_mounts` first.
- Use `FORGET` only for a stuck local disk; it does not drain a pool member (#5.2).
- Prefer `MOVE PARTITION` to/from a local (or different-type) disk. Do not BACKUP/MOVE CAS data onto another S3 disk with the same data-source description (#4.1).
- On large pools run `clickhouse-disks cas-fsck --timeout … --partial` instead of `SYSTEM CAS FSCK`; do not issue FORGET/GC STOP while SQL FSCK is running (#3.1).
- Always pass an explicit raw CAS disk name to `SYSTEM CAS GC RUN` (#2.2). Treat one RUN as incomplete; reclamation needs multiple rounds and catalog stillness (#2.3).
- After changing `cas_*` XML, restart; do not trust `SYSTEM RELOAD CONFIG` (#1.1).
- Do not put `DiskEncrypted` in front of CAS (#1.2). Name the cache disk in `TO DISK`, not the raw CAS disk (#4.2).
- When `is_leader`/`last_success_age_seconds` look idle, read `system.cas_gc_log` Finish rows before acting (#2.1).

## Recommended fixes
- Reject nested/prefix-overlapping `server_root_id` values at validate and at decommission selection (#5.1, X.1).
- Return a payload window from `getStorageObjects`, or disable server-side copy on CA (#4.1).
- Give SQL FSCK a deadline, honor `KILL QUERY`, and drop `lifecycle_mutex` across I/O (#3.1).
- Revalidate only the target catalog row during GC ref cleanup; surface aborts on `system.cas_gc_log` (#2.3).
- Implement `applyNewSettings` for live-safe keys and log restart-required ones (#1.1).
- Deduplicate cache-wrapped disks in `SYSTEM CAS GC RUN` fan-out and in health rows (#2.2).
- Expose `ever_succeeded` and a GC-scheduler state (`running`/`stopped`) on `system.cas_mounts` (#2.1).
- Fail-fast at config if the CAS disk is wrapped by `DiskEncrypted` (#1.2).
- Make `FORGET` vs `DROP POOL MEMBER` names/help text state node-local vs pool-wide (#5.2).
