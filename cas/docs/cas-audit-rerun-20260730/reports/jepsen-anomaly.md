# jepsen-anomaly — re-run 2026-07-30

Re-verification of the original `cas-jepsen-anomaly-audit.md` (section 20 "Consolidated
findings") against the PR HEAD at `cas-audit-20260730` (tracks `altinity/cas-gc-rebuild`).
Focus: mapping Jepsen anomaly classes (missing-read, dirty-read, lost-update, stale-read,
split-brain, overwritten-write, failed-removal) onto CAS-001 / CAS-002 / CAS-020 / CAS-029 /
CAS-030 / CAS-035 / CAS-045 / CAS-051.

Note on the code base: since the original audit the write path has undergone a **major
refactor**. The old per-shard `RootShard` object + `casPut(shard)` protocol was replaced by
a per-namespace `RefTableState` snapshot-plus-log architecture (`Pool/CasRefLedger.cpp`)
whose durable primitives are conditional-create / conditional-overwrite objects gated by a
**local write fence** (`CasMountRuntime::mayMutate`, `CasMountRuntime::refAppendFenceOk`)
and fence-generation admission (`CasMountRuntime::fenceGeneration`,
`checkFenceOrThrow`). The fence deadline is now anchored on `CLOCK_BOOTTIME`
(`CasMountRuntime::bootMsNow`), not wall-clock. This refactor materially changes several
Jepsen verdicts below.

## Scope in current code

- `Pool/CasRefLedger.{h,cpp}` — the per-namespace `RefTableState` append lane; where
  the old shard-level CAS lives now (durable log + snapshot objects).
- `Pool/CasMountRuntime.{h,cpp}` — the local write fence, fence-generation admission,
  `armMountFence`, `tripMountLost`, `bootMsNow`. Addresses J2/J3.
- `Pool/CasServerRoot.{h,cpp}` — `allocateWriterEpoch`, mount-lease claim/adopt,
  clean/dirty farewell, GC-fence certificate of death.
- `Pool/CasPool.{h,cpp}` — orchestration, `mayMutate`/`refAppendFenceOk` forwarders,
  `tryRemountOnce` (self-remount after GC fence-out), `fenceGeneration()`.
- `Backend/CasRequestControl.{h,cpp}` — the `CasRequestController` conditional-write
  primitive: pre-attempt fence check, PUT, post-write fence re-check with
  `CasConditionalWriteFenceLostPostWrite` accounting.
- `ContentAddressedMetadataStorage.cpp` — read path `getBlobViewPlan` / `readBlobPayload`
  (X1/R1 reader-pin surface).
- `Gc/CasGc.cpp`, `Gc/CasBlobInDegree.cpp` — condemn → `delete_pending` → exact-token
  `deleteExact`; ack-floor semantics.
- `ContentAddressedExchange.cpp` — relink / rename between server roots (cross-shard analogue).

## Findings still present

### `CAS-001` — Missing read (X1 / R1) — reader holds no pin across the deferred, unpinned blob GET

- Anchor: `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/ContentAddressedMetadataStorage.cpp:1886`
  (`getBlobViewPlan`) and `:1923` (`readBlobPayload`).
- Trigger: reader calls `getBlobViewPlan(path)`; the plan returns only a `StoredObject`
  and payload offsets. The manifest / ref view is discarded, no reader pin is registered
  on GC. The actual blob GET is issued later by `readObject` on a `StoredObject` alone.
  If between plan time and GET time a `dropRef` + GC round (condemn → `delete_pending`
  → `deleteExact`) fires, the deferred GET hits `NoSuchKey` mid-query for ref-less /
  cross-node readers.
- Evidence quote (`ContentAddressedMetadataStorage.cpp:1909-1917`):
  ```
  const auto location = snap.pool->locate(*entry);
  BlobViewPlan plan;
  plan.object = StoredObject(physicalKey(location.key), path, location.offset + location.length);
  plan.payload_offset = location.offset;
  plan.payload_end    = location.offset + location.length;
  return plan;
  ```
  The plan carries no pin token; nothing in `Gc/CasGc.cpp`'s condemn/graduation gate
  consults an active-reader set.
- Notes: I searched CAS for any `readerPin`, `acquireReaderPin`, `min_active`
  reader-side variant, `ackFloor` reader coupling — no matches. The ack-floor
  primitives that exist are for writer builds (`process_epoch`, `build_watermark`
  seq, `renewWatermarkOnce` in `CasPool.h:303`), not query lifetime. Same-node
  readers are still incidentally covered by MergeTree `DataPart` liveness /
  `old_parts_lifetime`; **ref-less and cross-node readers remain unprotected.**
  Jepsen mapping: **Missing read / Data loss — REACHABLE.** Class remains the one
  true committed-data-loss path in CAS.

### `CAS-002` — Split brain / zombie write — writer_epoch is still not the storage precondition

- Anchor: `Pool/CasRefLedger.cpp:145` (`stagingPutIfAbsent` →
  `ref_request_controller->putIfAbsentControlled(..., fence_ok_fn, ...)`),
  `:152` (`stagingConditionalCreate`), `:159` (`stagingConditionalOverwrite`),
  and `Backend/CasRequestControl.cpp:280-368` (`putIfAbsentControlled`).
- Trigger: two writer incarnations sharing a namespace / same key. The S3-level
  precondition is a **content token** (If-None-Match on the object key, or If-Match on
  the `Token` for `putOverwriteControlled`). The `writer_epoch` is NOT carried into the
  conditional PUT precondition; it is only used to **allocate a fresh table generation**
  (`liveWriterEpoch`, `CasPool.h:584`) and to gate the *local* write fence
  (`mount_runtime.mayMutate()`).
- Evidence quote (`Backend/CasRequestControl.cpp:299-368`):
  ```
  for (uint32_t attempt = 1; attempt <= budget.max_attempts; ++attempt)
  {
      if (!fence_ok())    return unresolved(...);      // pre-check
      ...
      committed_token = put->token;                    // conditional PUT (content token)
      ...
      if (!fence_ok())    // POST-check
      {
          ProfileEvents::increment(ProfileEvents::CasConditionalWriteFenceLostPostWrite);
          return unresolved(CasUnresolvedReason::FenceLostPostWrite);
      }
      return CasWriteOutcome::Committed;
  }
  ```
- Notes: this is a **strictly improved but still-soft** fence.
  (1) Pre-check `fence_ok` prevents *issuing* new writes after supersession.
  (2) Post-check turns a fence-loss-between-attempt-and-response into `Unresolved`
      (never `Committed`), so the *caller* is never told a superseded write succeeded.
  (3) `CasConditionalWriteFenceLostPostWrite` gives operational visibility.
  However: a paused writer that resumes with the fence still not tripped
  (network partition delayed the mount-lease renewer's supersession observation) can
  still ISSUE its PUT. The write may durably land at S3 before the local fence
  latches. Because the S3 CAS is content-token-based, the zombie's PUT succeeds if
  it hits an untouched key. The linearizability violation on the shard register
  (§8 "Register checker anomalies") therefore remains **REACHABLE** — smaller window,
  same shape. The report is still "CAS mount lost / lease expired — refusing to
  append" (`CasRefLedger.cpp:1337`), not a proper fencing-token rejection at the
  storage layer.
  Jepsen mapping: **Split brain / linearizability violation / zombie value / forked
  history — REACHABLE-BUT-NARROWED**, not fixed. The classical J1 fix (carry
  `writer_epoch` into every ref-object precondition, same pattern GC uses for
  `deleteExact`) is still open.

### `CAS-029` — VM-clone / snapshot split brain (same `server_uuid`)

- Anchor: `Pool/CasMountRuntime.cpp:133-140` (`armMountFence(server_uuid, writer_epoch,
  deadline_boot_ms)`), `Pool/CasServerRoot.cpp:180-260` (`allocateWriterEpoch` — same
  `server_uuid` different-epoch handling), `:806-830` (mount claim: rejects
  same-server-uuid different-epoch as superseded).
- Trigger: cloning a VM after `server_uuid` is materialized. Both nodes present the same
  UUID to the pool; today the CAS pool authenticates identity by `(server_uuid,
  writer_epoch)`, and the second-to-open incarnation forces a new epoch. Between the
  clone event and the second node acquiring a fresh epoch the two nodes are dual-mount
  under one identity.
- Evidence quote (`CasServerRoot.cpp:829-833`):
  ```
  "own mount slot fenced by GC after lease expiry — recoverable with a fresh writer_epoch"
  ```
  and (`:220-226`) a surviving-member observation forces
  `next_writer_epoch = max(1, surviving.writer_epoch + 1)`.
- Notes: J2 is BOUNDED but not IMMUNE. The window shrank because the fence deadline is
  now boot-clock (below), which advances during real elapsed time on both clones
  independently, so a clone taken while suspended does not import fence deadlines that
  survive resume. Verdict retained.
  Jepsen mapping: **Split brain (identity) — REACHABLE-BOUNDED.**

### `CAS-030` — Wall-clock mount-lease expiry vs boot-clock local fence — **FIXED (structurally)**

- Anchor: `Pool/CasMountRuntime.cpp:61-84` (`bootMs` = `CLOCK_BOOTTIME`,
  `mayMutate` compares `bootMsNow() < mount_fence.deadline_boot_ms`).
- Trigger (original): pause-and-resume of a VM breaks a wall-clock mount lease while
  a stale boot-clock local fence still permits writes.
- Evidence quote (`CasMountRuntime.cpp:61-70`):
  ```
  uint64_t CasMountRuntime::bootMs()
  {
      timespec ts{};
      clock_gettime(CLOCK_BOOTTIME, &ts);       // includes VM-suspend time
      ...
  }
  uint64_t CasMountRuntime::bootMsNow() const
  { return config.boot_ms_fn ? config.boot_ms_fn() : bootMs(); }
  ```
  and (`:84`): the fence predicate is `bootMsNow() < deadline_boot_ms.load()`.
- Notes: the fence deadline is now anchored on the **same physical clock** the
  mount-lease supersession relies on (`CLOCK_BOOTTIME` includes VM-suspend time on
  Linux, unlike `CLOCK_MONOTONIC`). Clock skew (NTP jump, wall-clock spoof) can no
  longer widen the local write fence beyond the true suspend-inclusive elapsed time.
  The write-side of J3 is thereby closed. The mount-lease *renewal cadence* is still
  wall-clock (`expires_at_ms`, `CasServerRoot.cpp:285`) but that is *observed* by the
  GC/other-node side and re-verified against boot-clock evidence of death; there is
  no wall-clock-only reclaim path.
  Jepsen mapping: **Split brain (clock) — FIXED for the local-fence side.** The
  mount-lease wall-clock exposure to NTP spoofing survives only on the *observer*
  side, and observation always requires a `certificate of death` — a passive skew
  never gets to reclaim (`CasServerRoot.cpp:409-418`).

### `CAS-035` — Presence-asserting closures misreport lost-ACK-succeeded write as failure — **LARGELY FIXED**

- Anchor: `Pool/CasRefLedger.cpp:1358-1420` (wedge resolution via
  `resolveByExactGet`), `:2801-2839` (`dropRef`).
- Trigger (original): `dropRef` re-reads its own committed drop and, on a lost-ACK, sees
  `FILE_DOESNT_EXIST` and misreports a durable success as a failure.
- Evidence quote (`CasRefLedger.cpp:2810-2820`):
  ```
  const auto it = state.getCommitted().find(ref_name);   // in-memory cached state,
                                                          // NOT a fresh S3 HEAD/GET
  ```
  wedge case handled by `resolveByExactGet(wedge_copy->key, wedge_copy->bytes)`
  (`:1398`) which reads exact bytes and treats a matched body as PROVES-DURABLE.
- Notes: the presence-asserting closure has been replaced by a cached-state
  in-memory read + a proper wedge-resolution primitive (`resolveByExactGet`) whose
  contract is exactly "matched key with matched bytes ⇒ durable success". A
  lost-ACK no longer degrades into a false FILE_DOESNT_EXIST for the *caller*.
  Jepsen mapping: **Request-dropped false-negative — FIXED for `dropRef`.**

### `CAS-045` — ZK part-set vs CAS ref can diverge on partial commit

- Anchor: n/a in CAS code; this straddles the ReplicatedMergeTree ↔ CAS ref boundary.
  Nearest CAS surface: `ContentAddressedExchange.cpp` (relink hand-off) and
  `ContentAddressedTransaction.cpp` (whole-part commit).
- Trigger: Zookeeper commit succeeds, CAS ref publish fails (or vice-versa). The
  CAS side of the boundary offers no atomic co-commit primitive to ZK; there is no
  ZK ↔ CAS reconciliation service.
- Notes: **REACHABLE — unchanged.** The refactor did not add a cross-plane
  reconciliation. Mitigated only by the fact that a CAS commit failure fails-closed
  the whole part transaction and the operator restart / fetch loop rebuilds — but
  the "ZK-has / CAS-missing" (broken part) and "CAS-has / ZK-missing" (invisible live
  ref leak) shapes remain.
  Jepsen mapping: **Fractured read across systems — REACHABLE.**

### `CAS-051` — Cross-region replicated shadow bucket

- Anchor: n/a in CAS code (backend concern). Nearest surface: `Backend/CasObjectStorageBackend.cpp`.
- Trigger: enabling S3 Cross-Region Replication on the CAS bucket creates a
  destination bucket that accumulates un-GC'd shadow objects. Failover onto it is
  token/ETag-incoherent (destination-side tokens are re-minted).
- Notes: no CAS-side detection or mitigation was added; still an operator hazard.
  Jepsen mapping: **Leak + split-brain-on-failover — REACHABLE.**

## Findings fixed / no longer reproducible

- `CAS-020` — **W1 (promote overwrite manifest leak) is FIXED.** The refactored append
  path uses `owner_transition(old_binding → new_binding)` semantics: the previous
  Committed binding is explicitly listed as `op.old_binding` and removed as part of the
  same log transaction that installs the new binding. See
  `CasRefLedger.cpp:2925-2926, 2932-2933` (drop path template applies to promote):
  ```
  op.kind = RefOpKind::OwnerTransition;
  op.old_binding = RefOwnerBinding{RefOwnerKind::Committed, ref_name, row.manifest_ref};
  ```
  and the "removal shrink state" comment at `:1805`. The prior manifest's blob-source
  edges therefore drop cleanly on promote; there is no unconditional `refs[R]=…`
  overwrite. `Jepsen: Overwritten write / Failed removal — SAFE for W1`.
  (The RENAME cross-shard non-atomicity is preserved BY-DESIGN, unchanged.)

- `CAS-030` — see above; the local write fence is now boot-clock-anchored.

- `CAS-035` — see above; `dropRef` reads authoritative in-memory state; wedge
  resolution is byte-exact.

## New findings (not in original audit)

- **NEW-jepsen-1** — *Post-write fence-loss surfaces as `Unresolved`, never
  `Committed`; but the durable object may exist and be visible to other mounts.*
  Severity: **Med (observability / operability).**
  Anchor: `Backend/CasRequestControl.cpp:361-365, 421-425, 487-489, 515-517,
  568-570, 596-598`.
  Trigger: a paused / superseded writer whose PUT lands after `fence_ok` starts
  returning false — the local return is `CasWriteOutcome::Unresolved` +
  `ProfileEvents::CasConditionalWriteFenceLostPostWrite` bump, but the OBJECT is
  durable on S3 and visible to any future reader that shares the key (all mounts
  of this pool). This is silently indistinguishable from CAS-002's zombie-write
  outcome on the storage plane. There is no compensating "unlink-what-you-just-put"
  step; the fence-lost writer just discards the outcome. Callers see Unresolved
  and typically retry against the fresh incarnation; the fresh incarnation then
  observes the zombie's byte-identical body via content-token dedup (no harm) OR a
  DIFFERENT body (silent divergence). *Recommended*: on FenceLostPostWrite, log the
  key and body-hash for post-incident audit; consider a best-effort DELETE against
  the exact token that would be a no-op if the object is unwritten.

- **NEW-jepsen-2** — *`fenceGeneration` admission covers the durable-effect blob
  finalize path only for `ContentAddressedTransaction::writeFile`; the ref-append
  lane relies on `fence_ok_fn` (boolean) rather than a captured generation token.*
  Severity: **Low (soft-vs-hard fence).**
  Anchor: `Pool/CasPool.h:328-337` (`fenceGeneration()` / `checkFenceOrThrow`) —
  documented as used by "the durable-effect site outside `CasPlainObjects`, i.e.
  the S3-native staging-buffer finalize"; `CasRefLedger.cpp:145-165` uses only
  `fence_ok_fn` boolean.
  Trigger: a rapid trip-latch → arm cycle (self-remount) between the pre-check
  and the S3 response would flip `fence_ok_fn` back to true, so the post-check
  would incorrectly succeed under the wrong incarnation. `fenceGeneration()`
  discriminates incarnations; using it on the ref append lane would tighten the
  post-check invariant from "fence is OK now" to "fence is OK *at the same
  generation we admitted under*".

- **NEW-jepsen-3** — *X1/R1 reader pin gap surface is unchanged; the refactor added
  no reader-side coupling to GC's ack floor.*
  Severity: **Med-High** (already CAS-001; called out as a NEW meta-finding because
  during the refactor the write side gained an ack-floor / build-watermark mechanism
  which is not extended to readers).
  Anchor: `Pool/CasPool.h:289-306` (per-server watermark surface documented as
  "writable-Pool build watermark", not query lifetime). Reader path
  `ContentAddressedMetadataStorage.cpp:1886-1933` never touches
  `renewWatermarkOnce` / `minActive`.
  Trigger: any deferred blob GET on a shared/cross-node read path (e.g.
  RESTORE from a snapshot, distributed SELECT, `FETCH` copy) is exposed to a
  concurrent GC delete round. The infrastructure exists (ack floor, exact-token
  delete gates); extending it with a "reader min-manifest-ref pin" folded into
  the union used by `graduateForDelete` is a clean fix but was not made.

## By-design / N/A / info

- **Cross-shard read-skew, phantoms, fractured read (RENAME)** — unchanged
  BY-DESIGN. CAS is per-object linearizable, not multi-object serializable.
  `Pool/CasRefLedger.cpp:2890-2939` (`dropNamespace` produces per-ref
  `owner_transition` removals but does not atomically bind cross-namespace state)
  confirms the contract.
- **`allow_stale` decode TTL vs GC latency (R3 in the original)** — the shard-level
  decode cache is gone under the RefTable refactor; `resolveRef`'s comment at
  `CasRefLedger.cpp:174-183` explicitly notes `allow_stale` no longer selects
  staleness: "this mounted writer is the ONLY writer of ns's ref state". The
  cross-server staleness dimension (an OTHER server's cached view) is now expressed
  differently and needs its own audit — flagged for cross-audit reconciliation.
- **Reader convoy (F-N1: coalesced shard read with no deadline)** — that read
  primitive was tied to the old shard-decode cache and appears removed in the
  refactor; leaving verdict to the read-protocol audit re-run.

## Verdict summary table

| CAS-id | Old severity | Old Jepsen mapping | Status | Evidence anchor |
|---|---|---|---|---|
| CAS-001 | Med-High | Missing read / data loss (X1/R1) | 🔴 still-present | `ContentAddressedMetadataStorage.cpp:1886, 1923` |
| CAS-002 | High | Split brain / zombie write / linearizability violation (J1) | 🔴 still-present (narrower) | `Backend/CasRequestControl.cpp:299-368`, `Pool/CasRefLedger.cpp:145-165` |
| CAS-020 | Med | Overwritten write / failed removal (W1) | ✅ fixed | `Pool/CasRefLedger.cpp:2925-2933` (`OwnerTransition` with `old_binding`) |
| CAS-029 | Med | Split brain (identity) (J2) | 🔴 still-present (bounded further by boot-clock) | `Pool/CasServerRoot.cpp:806-830`, `Pool/CasMountRuntime.cpp:133` |
| CAS-030 | Med | Split brain (clock) (J3) | ✅ fixed (local-fence side) | `Pool/CasMountRuntime.cpp:61-84` |
| CAS-035 | Med | Request-dropped false negative (W-N1) | ✅ fixed for `dropRef` | `Pool/CasRefLedger.cpp:2810-2820`, `:1398` |
| CAS-045 | Med | Fractured read across systems (ZK ↔ CAS) | 🔴 still-present | out-of-CAS (RMT integration) |
| CAS-051 | Med | Leak + split-brain on failover (cross-region) | 🔴 still-present | out-of-CAS (S3 backend) |
| NEW-jepsen-1 | Med | Silent durable object after `FenceLostPostWrite` | 🔴 new | `Backend/CasRequestControl.cpp:361-365` |
| NEW-jepsen-2 | Low | Ref lane uses boolean fence, not `fenceGeneration` token | 🔴 new | `Pool/CasPool.h:328-337`, `CasRefLedger.cpp:145-165` |
| NEW-jepsen-3 | Med-High | Reader pin gap unchanged despite write-side ack-floor infra | 🔴 new | `Pool/CasPool.h:289-306` vs `ContentAddressedMetadataStorage.cpp:1886-1933` |

### Counts

- Still-present (from original): **5** (CAS-001, CAS-002, CAS-029, CAS-045, CAS-051).
- Fixed / no longer reproducible: **3** (CAS-020, CAS-030, CAS-035).
- New findings: **3** (NEW-jepsen-1, -2, -3).
- By-design / N/A retained: cross-shard non-serializability, fractured RENAME.
